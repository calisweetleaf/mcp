"""
Web Tool - HTTP requests and web content fetching for MCP Server

This tool allows Copilot to gather information from the web,
download documentation, check APIs, and fetch any web resources.
Uses only Python standard library - no external dependencies.
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import logging
import time
import re
from typing import Dict, Optional, Any, Callable
from pathlib import Path


class WebTool:
    """Handles web requests and content fetching"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Web tool initialized")
        
        # Create cache directory
        self.cache_dir = Path("data/web_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Default headers to appear like a normal browser
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def fetch_url(self, url: str, headers: Optional[Dict[str, str]] = None, 
                 timeout: int = 30, max_size: int = 10*1024*1024) -> str:
        """Fetch content from a URL"""
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
                
                fetch_time = time.time() - start_time
                
                # Try to decode content
                try:
                    # Detect encoding
                    encoding = 'utf-8'
                    if content_type:
                        charset_match = re.search(r'charset=([^\s;]+)', content_type)
                        if charset_match:
                            encoding = charset_match.group(1)
                    
                    text_content = content.decode(encoding, errors='replace')
                    
                    # Format response
                    result = f"URL: {url}\n"
                    result += f"Status: {status_code}\n"
                    result += f"Content-Type: {content_type}\n"
                    result += f"Size: {len(content)} bytes\n"
                    result += f"Fetch time: {fetch_time:.2f} seconds\n"
                    result += f"Encoding: {encoding}\n\n"
                    
                    # Add content
                    if 'text/' in content_type or 'application/json' in content_type:
                        result += "CONTENT:\n" + text_content
                    else:
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
            except:
                return f"HTTP Error {e.code}: {e.reason}\nURL: {url}"
                
        except urllib.error.URLError as e:
            self.logger.error(f"URL error fetching {url}: {e.reason}")
            return f"URL Error: {e.reason}\nURL: {url}"
            
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return f"Error fetching {url}: {str(e)}"
    
    def download_file(self, url: str, filename: str, 
                     headers: Optional[Dict[str, str]] = None) -> str:
        """Download a file from URL to local filesystem"""
        try:
            # Validate inputs
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            file_path = Path(filename).expanduser().resolve()
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
        """Check if a URL is accessible and get basic info"""
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
        """Simple web search using DuckDuckGo's instant answer API"""
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
                    for i, topic in enumerate(search_data['RelatedTopics'][:num_results]):
                        if isinstance(topic, dict) and 'Text' in topic:
                            result += f"{i+1}. {topic['Text']}\n"
                            if 'FirstURL' in topic:
                                result += f"   URL: {topic['FirstURL']}\n"
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
        """Extract all links from a webpage"""
        try:
            # First fetch the content
            content = self.fetch_url(url)
            
            if content.startswith("Error:"):
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
    
    def get_tools(self) -> Dict[str, Callable]:
        """Return all available tool functions"""
        return {
            'bb7_fetch_url': lambda url, headers=None, timeout=30: 
                self.fetch_url(url, headers, timeout),
            'bb7_download_file': lambda url, filename, headers=None:
                self.download_file(url, filename, headers),
            'bb7_check_url_status': self.check_url_status,
            'bb7_search_web': lambda query, num_results=5:
                self.search_web(query, num_results),
            'bb7_extract_links': self.extract_links
        }


# For standalone testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    web = WebTool()
    
    # Test basic operations
    print(web.check_url_status("httpbin.org/status/200"))
    print("\n" + "="*50 + "\n")
    print(web.search_web("Python programming"))
    print("\n" + "="*50 + "\n")
    print(web.fetch_url("httpbin.org/json"))
