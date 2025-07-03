package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

// FPVClient represents a client for the FPV API
type FPVClient struct {
	baseURL string
	client  *http.Client
}

// PathBuilder maintains state for incremental path building
type PathBuilder struct {
	client    *FPVClient
	service   string
	basePath  string
	pathParts []string
	errors    []interface{}
	relative  bool
	fileAdded bool
}

// API request/response structures
type AddPartRequest struct {
	Service   string        `json:"service"`
	BasePath  string        `json:"base_path"`
	Parts     []string      `json:"parts"`
	Errors    []interface{} `json:"errors"`
	Validate  bool          `json:"validate"`
	Relative  bool          `json:"relative"`
	FileAdded bool          `json:"file_added"`
}

type AddPartResponse struct {
	Success     bool          `json:"success"`
	UpdatedPath string        `json:"updated_path"`
	NewErrors   []interface{} `json:"new_errors"`
	AllErrors   []interface{} `json:"all_errors"`
	PathParts   []string      `json:"path_parts"`
	Error       *string       `json:"error"`
}

type RemovePartRequest struct {
	Service   string        `json:"service"`
	BasePath  string        `json:"base_path"`
	PartIndex int           `json:"part_index"`
	Errors    []interface{} `json:"errors"`
	Relative  bool          `json:"relative"`
	FileAdded bool          `json:"file_added"`
}

type RemovePartResponse struct {
	Success         bool          `json:"success"`
	UpdatedPath     string        `json:"updated_path"`
	RemainingErrors []interface{} `json:"remaining_errors"`
	RemovedPart     *string       `json:"removed_part"`
	PathParts       []string      `json:"path_parts"`
	Error           *string       `json:"error"`
}

// NewFPVClient creates a new FPV API client
func NewFPVClient(baseURL string) *FPVClient {
	return &FPVClient{
		baseURL: baseURL,
		client: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// NewPathBuilder creates a new path builder for incremental path construction
func (c *FPVClient) NewPathBuilder(service, rootPath string, relative, fileAdded bool) *PathBuilder {
	return &PathBuilder{
		client:    c,
		service:   service,
		basePath:  rootPath,
		pathParts: []string{},
		errors:    []interface{}{},
		relative:  relative,
		fileAdded: fileAdded,
	}
}

// AddPart adds a path part and returns new errors
func (pb *PathBuilder) AddPart(part string) ([]interface{}, error) {
	req := AddPartRequest{
		Service:   pb.service,
		BasePath:  pb.basePath,
		Parts:     []string{part},
		Errors:    pb.errors,
		Validate:  true,
		Relative:  pb.relative,
		FileAdded: pb.fileAdded,
	}

	resp, err := pb.client.post("/path/add", req)
	if err != nil {
		return nil, err
	}

	var addResp AddPartResponse
	if err := json.Unmarshal(resp, &addResp); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %v", err)
	}

	if !addResp.Success {
		if addResp.Error != nil {
			return nil, fmt.Errorf("API error: %s", *addResp.Error)
		}
		return nil, fmt.Errorf("API request failed")
	}

	// Update state
	pb.basePath = addResp.UpdatedPath
	pb.pathParts = addResp.PathParts
	pb.errors = addResp.AllErrors

	return addResp.NewErrors, nil
}

// RemovePart removes a path part and returns remaining errors
func (pb *PathBuilder) RemovePart(index int) ([]interface{}, error) {
	req := RemovePartRequest{
		Service:   pb.service,
		BasePath:  pb.basePath,
		PartIndex: index,
		Errors:    pb.errors,
		Relative:  pb.relative,
		FileAdded: pb.fileAdded,
	}

	resp, err := pb.client.post("/path/remove", req)
	if err != nil {
		return nil, err
	}

	var removeResp RemovePartResponse
	if err := json.Unmarshal(resp, &removeResp); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %v", err)
	}

	if !removeResp.Success {
		if removeResp.Error != nil {
			return nil, fmt.Errorf("API error: %s", *removeResp.Error)
		}
		return nil, fmt.Errorf("API request failed")
	}

	// Update state
	pb.basePath = removeResp.UpdatedPath
	pb.pathParts = removeResp.PathParts
	pb.errors = removeResp.RemainingErrors

	return removeResp.RemainingErrors, nil
}

// GetCurrentPath returns the current full path
func (pb *PathBuilder) GetCurrentPath() string {
	return pb.basePath
}

// GetErrors returns all current errors
func (pb *PathBuilder) GetErrors() []interface{} {
	return pb.errors
}

// GetPathParts returns the current path parts
func (pb *PathBuilder) GetPathParts() []string {
	return pb.pathParts
}

// post makes a POST request to the API
func (c *FPVClient) post(endpoint string, data interface{}) ([]byte, error) {
	jsonData, err := json.Marshal(data)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %v", err)
	}

	url := c.baseURL + endpoint
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %v", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(body))
	}

	return body, nil
}

// Example usage for ByteWave integration
func main() {
	// Create FPV client
	fpv := NewFPVClient("http://localhost:8000/api/v1")

	// Create path builder for Windows
	builder := fpv.NewPathBuilder("windows", "C:\\", false, false)

	fmt.Println("🚀 ByteWave Path Builder Example")
	fmt.Println(strings.Repeat("=", 40))

	// Build path incrementally (like user typing)
	parts := []string{"Users", "golde", "Documents", "Project Files"}

	for i, part := range parts {
		fmt.Printf("\nAdding part %d: '%s'\n", i+1, part)

		newErrors, err := builder.AddPart(part)
		if err != nil {
			fmt.Printf("❌ Error: %v\n", err)
			break
		}

		fmt.Printf("✅ Current path: %s\n", builder.GetCurrentPath())
		if len(newErrors) > 0 {
			fmt.Printf("⚠️  New errors: %d\n", len(newErrors))
		} else {
			fmt.Printf("✅ No new errors\n")
		}
	}

	// Add a file
	fmt.Printf("\nAdding file: 'document.txt'\n")
	builder.fileAdded = true
	newErrors, err := builder.AddPart("document.txt")
	if err != nil {
		fmt.Printf("❌ Error: %v\n", err)
	} else {
		fmt.Printf("✅ Final path: %s\n", builder.GetCurrentPath())
		if len(newErrors) > 0 {
			fmt.Printf("⚠️  New errors: %d\n", len(newErrors))
		}
	}

	// Remove a part
	fmt.Printf("\nRemoving part at index 2\n")
	remainingErrors, err := builder.RemovePart(2)
	if err != nil {
		fmt.Printf("❌ Error: %v\n", err)
	} else {
		fmt.Printf("✅ Path after removal: %s\n", builder.GetCurrentPath())
		fmt.Printf("Remaining errors: %d\n", len(remainingErrors))
	}

	fmt.Printf("\n🎉 Path building completed!\n")
	fmt.Printf("Final path: %s\n", builder.GetCurrentPath())
	fmt.Printf("Total errors: %d\n", len(builder.GetErrors()))
}
