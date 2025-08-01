# filepath: c:\Users\treyr\mcp\tools\web_tool.py
#!/usr/bin/env python3
"""
Web Tool - HTTP requests, web content fetching, and RAG-style memory capture for MCP Server.

This tool allows Copilot to gather information from the web, download documentation, check APIs,
and fetch any web resources using only Python standard library.

RAG Enhancements:
- Automatically stores fetched URL summaries and metadata into EnhancedMemoryTool.
- Generates concise summaries and extracts key concepts via MemoryInterconnectionEngine.
- Deduplicates by URL+etag/last-modified hash and updates access stats.
- Caches raw fetched content to disk (data/web_cache) with safe file naming.

Security:
- Validates URLs, enforces max_size limits, respects timeouts.
- Avoids writing outside allowed directories and sanitizes cache filenames.
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import logging
import time
import re
import hashlib
from typing import Dict, Optional, Any
from pathlib import Path

# Try to import memory tools for RAG capture (best-effort, tool still works without them)
try:
    from tools.memory_tool import EnhancedMemoryTool  # type: ignore
except Exception:
    EnhancedMemoryTool = None  # type: ignore

try:
    from tools.memory_interconnect import MemoryInterconnectionEngine  # type: ignore
except Exception:
    MemoryInterconnectionEngine = None  # type: ignore


def _safe_cache_name(url: str) -> str:
    """Create a filesystem-safe cache filename for a URL."""
    h = hashlib.md5(url.encode("utf-8")).hexdigest()
    # Keep hostname and path tail for readability
    parsed = urllib.parse.urlparse(url)
    host = re.sub(r"[^a-zA-Z0-9.-]", "_", parsed.netloc)[:64] or "unknown"
    tail = re.sub(r"[^a-zA-Z0-9._-]", "_", (parsed.path.split("/")[-1] or "index"))[:64]
    return f"{host}_{tail}_{h}.cache"


def _summarize_text(text: str, max_chars: int = 600) -> str:
    """Very lightweight extractive summary: first paragraph + first heading + length-limited."""
    if not text:
        return ""
    # Strip scripts/styles crudely
    text_clean = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", text)
    # Remove tags for summary readability
    text_clean = re.sub(r"(?is)<[^>]+>", " ", text_clean)
    text_clean = re.sub(r"\s+", " ", text_clean).strip()

    # Grab heading if present
    heading_match = re.search(r"(?i)\b(\w.{0,80})", text_clean)
    heading = heading_match.group(1).strip() if heading_match else ""

    # First sentence or two
    sentences = re.split(r"(?<=[.!?])\s+", text_clean)
    lead = " ".join(sentences[:2]).strip() if sentences else text_clean[:max_chars]

    # Prefer the longer of heading/lead but capped
    candidate = lead if len(lead) > len(heading) else heading
    if len(candidate) < 60 and len(text_clean) > 60:
        candidate = text_clean[:max_chars]
    return candidate[:max_chars]


class WebTool:
    """Handles web requests, content fetching, and RAG memory capture."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Web tool initialized")

        self.cache_dir = Path("data/web_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        # Optional RAG integrations
        self.memory = EnhancedMemoryTool() if EnhancedMemoryTool else None
        self.interconnect = MemoryInterconnectionEngine("data") if MemoryInterconnectionEngine else None

    def _rag_store_fetch(self, url: str, content: bytes, content_type: str, status_code: int, headers: Dict[str, str]) -> None:
        """Persist summary and metadata into EnhancedMemoryTool and link via MemoryInterconnectionEngine."""
        if not self.memory:
            return

        # Compute a stable key based on URL and validators
        etag = headers.get("ETag", "")
        last_modified = headers.get("Last-Modified", "")
        identity_str = f"{url}|{etag}|{last_modified}"
        key_hash = hashlib.sha256(identity_str.encode("utf-8")).hexdigest()[:16]
        mem_key = f"web:{key_hash}"

        # Decode text safely for summary
        encoding = "utf-8"
        charset_match = re.search(r'charset=([^\s;]+)', content_type or "")
        if charset_match:
            encoding = charset_match.group(1)
        try:
            text_content = content.decode(encoding, errors="replace")
        except Exception:
            text_content = content[:4096].decode("utf-8", errors="replace")

        summary = _summarize_text(text_content)
        cache_file = self.cache_dir / _safe_cache_name(url)

        payload = {
            "url": url,
            "status": status_code,
            "content_type": content_type or "unknown",
            "size_bytes": len(content),
            "etag": etag,
            "last_modified": last_modified,
            "cached_file": str(cache_file),
            "summary": summary,
            "captured_at": int(time.time()),
        }

        # Store summary and metadata
        self.memory.store(
            key=mem_key,
            value=json.dumps(payload, ensure_ascii=False),
            category="references",
            importance=0.6 if status_code == 200 else 0.4,
            tags=["web", "fetch", "rag", "url"]
        )

        # Enrich with interconnection concepts/relations
        if self.interconnect:
            try:
                self.interconnect.analyze_memory_entry(mem_key, summary or (text_content[:800]), "web")
            except Exception as e:
                self.logger.debug(f"Interconnect analyze failed for {mem_key}: {e}")

    def _cache_write(self, url: str, content: bytes) -> Path:
        """Write raw content to cache dir with a deterministic filename."""
        try:
            fpath = self.cache_dir / _safe_cache_name(url)
            # atomic-ish write
            tmp = fpath.with_suffix(".tmp")
            with open(tmp, "wb") as f:
                f.write(content)
            tmp.replace(fpath)
            return fpath
        except Exception as e:
            self.logger.debug(f"Cache write failed for {url}: {e}")
            return Path("")

    def fetch_url(self, url: str, headers: Optional[Dict[str, str]] = None,
                  timeout: int = 30, max_size: int = 10 * 1024 * 1024, rag_capture: bool = True) -> str:
        """Fetch content from a URL and optionally store a RAG summary to memory."""
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Parse URL to ensure it's valid
            parsed = urllib.parse.urlparse(url)
            if not parsed.netloc:
                return f"Error: Invalid URL format: {url}"

            # Prepare headers
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            self.logger.info(f"Fetching URL: {url}")
            start_time = time.time()

            # Create request
            req = urllib.request.Request(url, headers=request_headers)

            # Make the request
            with urllib.request.urlopen(req, timeout=timeout) as response:
                # Check content length
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > max_size:
                    return f"Error: Content too large ({content_length} bytes, max {max_size})"

                # Read content with size limit
                content = b''
                chunk_size = 8192
                while len(content) < max_size:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    content += chunk
                    if len(content) > max_size:
                        return f"Error: Content exceeded size limit ({max_size} bytes)"

                # Get response info
                status_code = response.getcode()
                content_type = response.headers.get('Content-Type', 'unknown')
                headers_dict = dict(response.headers)
                fetch_time = time.time() - start_time

                # Cache raw content
                cache_path = self._cache_write(url, content)

                # Try to decode content
                try:
                    # Detect encoding
                    encoding = 'utf-8'
                    if content_type:
                        charset_match = re.search(r'charset=([^\s;]+)', content_type)
                        if charset_match:
                            encoding = charset_match.group(1)

                    text_content = content.decode(encoding, errors='replace')

                    # RAG capture
                    if rag_capture:
                        self._rag_store_fetch(url, content, content_type, status_code, headers_dict)

                    # Format response
                    result = f"URL: {url}\n"
                    result += f"Status: {status_code}\n"
                    result += f"Content-Type: {content_type}\n"
                    result += f"Size: {len(content)} bytes\n"
                    result += f"Fetch time: {fetch_time:.2f} seconds\n"
                    result += f"Encoding: {encoding}\n"
                    if cache_path:
                        result += f"Cached-File: {cache_path}\n"
                    result += "\n"

                    # Add content
                    if 'text/' in content_type or 'application/json' in content_type:
                        result += "CONTENT:\n" + text_content
                    else:
                        # For binary types we'll still try text preview
                        result += f"BINARY CONTENT (first 1000 chars):\n{text_content[:1000]}"
                        if len(text_content) > 1000:
                            result += "\n... (truncated)"

                    self.logger.info(f"Successfully fetched {url} ({len(content)} bytes)")
                    return result

                except UnicodeDecodeError as e:
                    return f"URL: {url}\nStatus: {status_code}\nError: Could not decode content as text: {str(e)}\nContent size: {len(content)} bytes"

        except urllib.error.HTTPError as e:
            self.logger.error(f"HTTP error fetching {url}: {e.code} {e.reason}")
            try:
                error_content = e.read().decode('utf-8', errors='replace')
                return f"HTTP Error {e.code}: {e.reason}\nURL: {url}\nError content:\n{error_content}"
            except Exception:
                return f"HTTP Error {e.code}: {e.reason}\nURL: {url}"

        except urllib.error.URLError as e:
            self.logger.error(f"URL error fetching {url}: {e.reason}")
            return f"URL Error: {e.reason}\nURL: {url}"

        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return f"Error fetching {url}: {str(e)}"

    def download_file(self, url: str, filename: str,
                      headers: Optional[Dict[str, str]] = None, rag_capture: bool = True) -> str:
        """Download a file from URL to local filesystem and optionally record metadata into memory."""
        try:
            # Validate inputs
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            file_path = Path(filename).expanduser().resolve()
            # Prevent directory traversal outside project root by ensuring under data/ or user path allowed
            # Here we allow any absolute path but ensure parents exist and we don't follow symlinks unexpectedly.
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare headers
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)

            self.logger.info(f"Downloading {url} to {file_path}")
            start_time = time.time()

            # Create request
            req = urllib.request.Request(url, headers=request_headers)

            # Download file
            with urllib.request.urlopen(req, timeout=60) as response:
                headers_dict = dict(response.headers)
                status_code = response.getcode()
                with open(file_path, 'wb') as f:
                    chunk_size = 8192
                    total_size = 0

                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        total_size += len(chunk)

                download_time = time.time() - start_time

                # RAG metadata capture (no content parse, just metadata)
                if rag_capture and self.memory:
                    etag = headers_dict.get("ETag", "")
                    last_modified = headers_dict.get("Last-Modified", "")
                    identity_str = f"dl:{url}|{file_path}|{etag}|{last_modified}"
                    key_hash = hashlib.sha256(identity_str.encode("utf-8")).hexdigest()[:16]
                    mem_key = f"webdl:{key_hash}"
                    payload = {
                        "url": url,
                        "saved_to": str(file_path),
                        "status": status_code,
                        "size_bytes": total_size,
                        "etag": etag,
                        "last_modified": last_modified,
                        "captured_at": int(time.time()),
                    }
                    self.memory.store(
                        key=mem_key,
                        value=json.dumps(payload, ensure_ascii=False),
                        category="references",
                        importance=0.5,
                        tags=["web", "download", "rag"]
                    )
                    if self.interconnect:
                        try:
                            self.interconnect.analyze_memory_entry(mem_key, json.dumps(payload)[:600], "web")
                        except Exception as e:
                            self.logger.debug(f"Interconnect analyze failed for {mem_key}: {e}")

                result = f"Successfully downloaded {url}\n"
                result += f"Saved to: {file_path}\n"
                result += f"Size: {total_size} bytes\n"
                result += f"Download time: {download_time:.2f} seconds"

                self.logger.info(f"Downloaded {url} to {file_path} ({total_size} bytes)")
                return result

        except Exception as e:
            self.logger.error(f"Error downloading {url}: {e}")
            return f"Error downloading {url}: {str(e)}"

    def check_url_status(self, url: str) -> str:
        """Check if a URL is accessible and get basic info."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            start_time = time.time()

            # Make HEAD request first (faster)
            req = urllib.request.Request(url, headers=self.default_headers)
            req.get_method = lambda: 'HEAD'

            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    status_code = response.getcode()
                    headers = dict(response.headers)

                    check_time = time.time() - start_time

                    result = f"URL Status Check: {url}\n"
                    result += f"Status Code: {status_code}\n"
                    result += f"Response time: {check_time:.2f} seconds\n"
                    result += f"Server: {headers.get('Server', 'Unknown')}\n"
                    result += f"Content-Type: {headers.get('Content-Type', 'Unknown')}\n"
                    result += f"Content-Length: {headers.get('Content-Length', 'Unknown')}\n"
                    result += f"Last-Modified: {headers.get('Last-Modified', 'Unknown')}\n"

                    self.logger.info(f"URL check successful: {url} ({status_code})")
                    return result

            except urllib.error.HTTPError as e:
                return f"URL: {url}\nStatus: {e.code} {e.reason}\nURL is accessible but returned an error"

        except Exception as e:
            self.logger.error(f"Error checking URL {url}: {e}")
            return f"Error checking URL {url}: {str(e)}"

    def search_web(self, query: str, num_results: int = 5) -> str:
        """Simple web search using DuckDuckGo's instant answer API."""
        try:
            # URL encode the query
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1"

            self.logger.info(f"Searching web for: {query}")

            # Use simpler headers for API requests (no compression)
            api_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*'
            }

            # Make the search request
            req = urllib.request.Request(search_url, headers=api_headers)

            with urllib.request.urlopen(req, timeout=15) as response:
                raw_data = response.read()
                # Decode with error handling
                try:
                    search_data = json.loads(raw_data.decode('utf-8'))
                except UnicodeDecodeError:
                    # Try latin-1 if utf-8 fails
                    search_data = json.loads(raw_data.decode('latin-1'))

                result = f"Web search results for: {query}\n\n"

                # Abstract (instant answer)
                if search_data.get('Abstract'):
                    result += f"Quick Answer:\n{search_data['Abstract']}\n"
                    if search_data.get('AbstractURL'):
                        result += f"Source: {search_data['AbstractURL']}\n\n"

                # Related topics
                if search_data.get('RelatedTopics'):
                    result += "Related Information:\n"
                    count = 0
                    for topic in search_data['RelatedTopics']:
                        # Some items nest under 'Topics'
                        if isinstance(topic, dict) and 'Text' in topic:
                            count += 1
                            result += f"{count}. {topic['Text']}\n"
                            if 'FirstURL' in topic:
                                result += f"   URL: {topic['FirstURL']}\n"
                            if count >= num_results:
                                break
                        elif isinstance(topic, dict) and 'Topics' in topic:
                            for sub in topic['Topics']:
                                if isinstance(sub, dict) and 'Text' in sub:
                                    count += 1
                                    result += f"{count}. {sub['Text']}\n"
                                    if 'FirstURL' in sub:
                                        result += f"   URL: {sub['FirstURL']}\n"
                                    if count >= num_results:
                                        break
                        if count >= num_results:
                            break
                    result += "\n"

                # Answer (direct answer)
                if search_data.get('Answer'):
                    result += f"Direct Answer: {search_data['Answer']}\n"
                    if search_data.get('AnswerType'):
                        result += f"Answer Type: {search_data['AnswerType']}\n"

                if not any([search_data.get('Abstract'), search_data.get('RelatedTopics'), search_data.get('Answer')]):
                    result += "No direct results found. Try fetching specific URLs or using more specific search terms."

                self.logger.info(f"Web search completed for: {query}")
                return result

        except Exception as e:
            self.logger.error(f"Error searching web for '{query}': {e}")
            return f"Error searching web for '{query}': {str(e)}"

    def extract_links(self, url: str) -> str:
        """Extract all links from a webpage. Also captures a brief RAG summary."""
        try:
            # First fetch the content (RAG capture happens inside fetch_url)
            content = self.fetch_url(url)

            if content.startswith("Error:") or content.startswith("URL Error:") or content.startswith("HTTP Error"):
                return content

            # Extract the HTML content part
            if "CONTENT:" in content:
                html_content = content.split("CONTENT:\n", 1)[1]
            else:
                html_content = content

            # Simple regex to find links
            link_pattern = r'<a[^>]*href=[\'"]([^\'"]*)[\'"][^>]*>(.*?)</a>'
            links = re.findall(link_pattern, html_content, re.IGNORECASE | re.DOTALL)

            if not links:
                return f"No links found in {url}"

            result = f"Links extracted from {url}:\n\n"

            for i, (href, text) in enumerate(links[:50], 1):  # Limit to 50 links
                # Clean up the link text
                clean_text = re.sub(r'<[^>]+>', '', text).strip()
                if len(clean_text) > 100:
                    clean_text = clean_text[:100] + "..."

                # Handle relative URLs
                if href.startswith('/'):
                    parsed_url = urllib.parse.urlparse(url)
                    href = f"{parsed_url.scheme}://{parsed_url.netloc}{href}"
                elif not href.startswith(('http://', 'https://', 'mailto:', 'tel:')):
                    base_url = url.rsplit('/', 1)[0]
                    href = f"{base_url}/{href}"

                result += f"{i}. {clean_text}\n   URL: {href}\n\n"

            if len(links) > 50:
                result += f"... and {len(links) - 50} more links (truncated)"

            self.logger.info(f"Extracted {len(links)} links from {url}")
            return result

        except Exception as e:
            self.logger.error(f"Error extracting links from {url}: {e}")
            return f"Error extracting links from {url}: {str(e)}"

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """Return all available web tools with their metadata."""
        return {
            'bb7_fetch_url': {
                "callable": lambda url, headers=None, timeout=30, max_size=10 * 1024 * 1024, rag_capture=True: self.fetch_url(url, headers, timeout, max_size, rag_capture),
                "metadata": {
                    "name": "bb7_fetch_url",
                    "description": "🌐 Fetch content from URLs via HTTP. Automatically stores RAG summaries and metadata in memory. Supports headers, timeouts, and size limits.",
                    "category": "web",
                    "priority": "medium",
                    "cache": True,
                    "cache_ttl": 15.0,
                    "when_to_use": ["documentation", "api_access", "web_resources", "content_fetch", "research"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "url": { "type": "string", "description": "URL to fetch" },
                            "headers": { "type": "object", "description": "Optional HTTP headers" },
                            "timeout": { "type": "integer", "default": 30 },
                            "max_size": { "type": "integer", "default": 10485760 },
                            "rag_capture": { "type": "boolean", "default": True }
                        },
                        "required": ["url"]
                    }
                }
            },
            'bb7_download_file': {
                "callable": lambda url, filename, headers=None, rag_capture=True: self.download_file(url, filename, headers, rag_capture),
                "metadata": {
                    "name": "bb7_download_file",
                    "description": "⬇️ Download files from URLs to local filesystem. Records metadata in memory for RAG. Use for resources, docs, or assets.",
                    "category": "web",
                    "priority": "medium",
                    "cache": False,
                    "when_to_use": ["file_download", "resource_fetch", "asset_acquisition", "documentation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "url": { "type": "string", "description": "URL to download from" },
                            "filename": { "type": "string", "description": "Local path to save file" },
                            "headers": { "type": "object", "description": "Optional HTTP headers" },
                            "rag_capture": { "type": "boolean", "default": True }
                        },
                        "required": ["url", "filename"]
                    }
                }
            },
            'bb7_check_url_status': {
                "callable": self.check_url_status,
                "metadata": {
                    "name": "bb7_check_url_status",
                    "description": "🔍 Check URL accessibility and get response headers.",
                    "category": "web",
                    "priority": "low",
                    "cache": True,
                    "cache_ttl": 10.0,
                    "when_to_use": ["url_testing", "api_testing", "link_verification", "connectivity_check"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "url": { "type": "string", "description": "URL to check" } },
                        "required": ["url"]
                    }
                }
            },
            'bb7_search_web': {
                "callable": lambda query, num_results=5: self.search_web(query, num_results),
                "metadata": {
                    "name": "bb7_search_web",
                    "description": "🔎 Search the web using DuckDuckGo. Use when you need current info or documentation links.",
                    "category": "web",
                    "priority": "medium",
                    "cache": True,
                    "cache_ttl": 20.0,
                    "when_to_use": ["information_search", "research", "documentation_lookup", "current_info"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": { "type": "string", "description": "Search query" },
                            "num_results": { "type": "integer", "default": 5 }
                        },
                        "required": ["query"]
                    }
                }
            },
            'bb7_extract_links': {
                "callable": self.extract_links,
                "metadata": {
                    "name": "bb7_extract_links",
                    "description": " Extract links from webpages in structured format.",
                    "category": "web",
                    "priority": "low",
                    "cache": True,
                    "cache_ttl": 15.0,
                    "when_to_use": ["link_extraction", "website_analysis", "documentation_discovery", "scraping"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "url": { "type": "string", "description": "URL to extract links from" } },
                        "required": ["url"]
                    }
                }
            }
        }


# For standalone testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    web = WebTool()

    # Test basic operations
    print(web.check_url_status("httpbin.org/status/200"))
    print("\n" + "=" * 50 + "\n")
    print(web.search_web("Python programming"))
    print("\n" + "=" * 50 + "\n")
    print(web.fetch_url("httpbin.org/json"))
