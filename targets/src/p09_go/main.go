package main

// Prints a greeting and a name-based UUID. Flags: --name (default "world"), --count (default 1).
// The UUID is version 5 (SHA-1 of the name in the DNS namespace). count below 1 exits with code 3.

import (
	"fmt"
	"os"

	"github.com/google/uuid"
	"github.com/spf13/pflag"
)

func main() {
	name := pflag.String("name", "world", "who to greet")
	n := pflag.Int("count", 1, "how many times")
	pflag.Parse()
	id := uuid.NewSHA1(uuid.NameSpaceDNS, []byte(*name))
	for i := 0; i < *n; i++ {
		fmt.Printf("hello %s %s\n", *name, id)
	}
	if *n < 1 {
		os.Exit(3)
	}
}
