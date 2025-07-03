# FPV API Integration Examples

This directory contains examples of how to integrate with the FPV API from different programming languages and frameworks.

## Examples

### Go Client (`go_client_example.go`)
A complete Go client demonstrating how ByteWave or other Go applications can integrate with the FPV dynamic path building API.

**Features:**
- Incremental path building with state management
- Error tracking and propagation
- Async-friendly HTTP client
- Type-safe request/response handling

**Usage:**
```bash
cd examples
go run go_client_example.go
```

**Key Benefits for ByteWave:**
- **O(1) validation per path part** - only validate new additions
- **Lightweight state management** - minimal memory footprint
- **Real-time feedback** - validate as user types
- **Cross-platform support** - same API for all storage providers

### Python Test Script (`../test_dynamic_api.py`)
Comprehensive test script demonstrating all dynamic path building endpoints with performance testing.

**Features:**
- Incremental path building tests
- Concurrent request testing
- Error handling scenarios
- Performance benchmarking

**Usage:**
```bash
python test_dynamic_api.py
```

## Integration Patterns

### 1. Stateful Path Builder
Maintain a lightweight state object that tracks:
- Current path parts
- Error state
- Service configuration

### 2. Incremental Validation
Only validate new path parts, not entire paths:
```go
// Instead of revalidating entire path
// Just validate the new part
newErrors, err := builder.AddPart("new_folder")
```

### 3. Error Propagation
Track and propagate errors efficiently:
```go
// Combine existing errors with new ones
allErrors = append(existingErrors, newErrors...)
```

### 4. Async Operations
Use non-blocking API calls for UI responsiveness:
```go
// Can be called from UI thread
go func() {
    newErrors, err := builder.AddPart(part)
    // Update UI with results
}()
```

## Performance Considerations

### Memory Usage
- **Client State**: ~1KB per path builder instance
- **API Response**: ~2-5KB per request
- **Error Objects**: ~100-500 bytes per error

### Network Efficiency
- **Request Size**: ~200-500 bytes per request
- **Response Time**: ~5-20ms on localhost
- **Concurrent Requests**: 100+ requests/second

### Caching Strategy
Consider caching validation results for common path patterns:
```go
// Cache validation results
cacheKey := fmt.Sprintf("%s:%s", service, pathPart)
if cached, exists := cache[cacheKey]; exists {
    return cached
}
```

## Error Handling

### API Errors
- **400**: Invalid request parameters
- **500**: Server-side validation errors
- **Network**: Connection timeouts, DNS failures

### Validation Errors
- **Invalid characters**: Removed or replaced
- **Length violations**: Truncated automatically
- **Platform-specific**: Service-specific rules

## Best Practices

1. **Start with root path**: Begin with platform-appropriate root
2. **Validate incrementally**: Check each part as it's added
3. **Handle errors gracefully**: Show user-friendly error messages
4. **Cache when possible**: Store validation results for performance
5. **Use appropriate timeouts**: Set reasonable HTTP timeouts
6. **Monitor performance**: Track API response times

## ByteWave Integration

For ByteWave specifically, this API provides:

✅ **No Go port needed** - Keep FPV in Python where it's mature  
✅ **Real-time validation** - Validate as user builds paths  
✅ **Cross-platform support** - Same API for all storage providers  
✅ **Performance optimized** - O(1) validation per path part  
✅ **Async-friendly** - Non-blocking operations for UI  
✅ **Lightweight integration** - Minimal Go code required  

The dynamic path building endpoints eliminate the need for a full Go port while providing all the performance benefits of incremental validation. 