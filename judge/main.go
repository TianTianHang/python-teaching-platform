package main

import (
    "net/http"
    "log"
)

func main() {
    http.HandleFunc("/run", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte(`{"status": "ok", "output": "Hello from Go Judge!"}`))
    })
    log.Println("Judge service running on :8081")
    http.ListenAndServe(":8081", nil)
}