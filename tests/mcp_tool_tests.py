# Testing MCP Tools

## Memory Tools Testing

### 1. Testing memory_store
```python
result = memory_store(key='test_key', value='test_value')
print(result)
```

### 2. Testing memory_retrieve
```python
result = memory_retrieve(key='test_key')
print(result)
```

### 3. Testing memory_list
```python
result = memory_list()
print(result)
```

### 4. Testing memory_delete
```python
result = memory_delete(key='test_key')
print(result)
```

### 5. Testing memory_stats
```python
result = memory_stats()
print(result)
```

## File Operations Testing

### 1. Testing read_file
```python
result = read_file('test.txt')
print(result)
```

### 2. Testing write_file
```python
result = write_file('test.txt', 'Hello World!')
print(result)
```

### 3. Testing append_file
```python
result = append_file('test.txt', ' Appending this text.')
print(result)
```

### 4. Testing list_directory
```python
result = list_directory('.')
print(result)
```

### 5. Testing get_file_info
```python
result = get_file_info('test.txt')
print(result)
```

### 6. Testing search_files
```python
result = search_files('*.txt')
print(result)
```

## Shell & System Tools Testing

### 1. Testing run_command
```python
result = run_command('echo Hello')
print(result)
```

### 2. Testing run_script
```python
result = run_script('test_script.py')
print(result)
```

### 3. Testing get_environment
```python
result = get_environment()
print(result)
```

### 4. Testing list_processes
```python
result = list_processes()
print(result)
```

### 5. Testing kill_process
```python
result = kill_process(pid=1234)
print(result)
```

### 6. Testing get_system_info
```python
result = get_system_info()
print(result)
```

## Web & Network Tools Testing

### 1. Testing fetch_url
```python
result = fetch_url('https://example.com')
print(result)
```

### 2. Testing download_file
```python
result = download_file('https://example.com/test.txt')
print(result)
```

### 3. Testing check_url_status
```python
result = check_url_status('https://example.com')
print(result)
```

### 4. Testing search_web
```python
result = search_web('GitHub Copilot')
print(result)
```

### 5. Testing extract_links
```python
result = extract_links('https://example.com')
print(result)
```

## Session Management Tools Testing

### 1. Testing start_session
```python
result = start_session('Testing session')
print(result)
```

### 2. Testing log_event
```python
result = log_event('Event logged')
print(result)
```

### 3. Testing capture_insight
```python
result = capture_insight('Insight captured')
print(result)
```

### 4. Testing record_workflow
```python
result = record_workflow('Workflow recorded')
print(result)
```

### 5. Testing update_focus
```python
result = update_focus('Focusing on task')
print(result)
```

### 6. Testing pause_session
```python
result = pause_session('Taking a break')
print(result)
```

### 7. Testing resume_session
```python
result = resume_session()
print(result)
```

### 8. Testing list_sessions
```python
result = list_sessions()
print(result)
```

### 9. Testing get_session_summary
```python
result = get_session_summary()
print(result)
```

## Visual Partnership Tools Testing

### 1. Testing bb7_screen_capture
```python
result = bb7_screen_capture()
print(result)
```

### 2. Testing bb7_keyboard_input
```python
result = bb7_keyboard_input('Hello')
print(result)
```

### 3. Testing bb7_mouse_control
```python
result = bb7_mouse_control('click')
print(result)
```

### 4. Testing bb7_window_manager
```python
result = bb7_window_manager('focus')
print(result)
```

### 5. Testing bb7_clipboard_manage
```python
result = bb7_clipboard_manage('copy', 'Text to copy')
print(result)
```

### 6. Testing bb7_visual_diff
```python
result = bb7_visual_diff('screenshot1.png', 'screenshot2.png')
print(result)
```

### 7. Testing bb7_screen_monitor
```python
result = bb7_screen_monitor()
print(result)
```

## VS Code Terminal Integration Testing

### 1. Testing bb7_terminal_status
```python
result = bb7_terminal_status()
print(result)
```

### 2. Testing bb7_terminal_run_command
```python
result = bb7_terminal_run_command('echo Test command')
print(result)
```

### 3. Testing bb7_terminal_history
```python
result = bb7_terminal_history(limit=5)
print(result)
```

### 4. Testing bb7_terminal_environment
```python
result = bb7_terminal_environment()
print(result)
```

### 5. Testing bb7_terminal_cd
```python
result = bb7_terminal_cd('..')
print(result)
```

### 6. Testing bb7_terminal_which
```python
result = bb7_terminal_which('python')
print(result)
```
