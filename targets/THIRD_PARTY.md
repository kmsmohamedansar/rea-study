# Third-party code in the targets

Retrieved 2026-10-19 from the upstream default branch (not a tagged release), copied unchanged except the small `main.c` we wrote next to each. Licence texts are copied beside the code. SHA-256 below lets anyone check the files are unmodified.

| target | what | upstream | licence | files (sha256, first 16 hex) |
|---|---|---|---|---|
| p06_sha256 | SHA-256 (Brad Conte, crypto-algorithms) | github.com/B-Con/crypto-algorithms | public domain (README: released into the public domain free of any restrictions; text in LICENSE-NOTE.txt) | sha256.c `4cbc93d30c28cee2`; sha256.h `a946e621775fd825`; |
| p07_tinyexpr | tinyexpr expression evaluator | github.com/codeplea/tinyexpr | zlib (LICENSE) | tinyexpr.c `ae8a179cf65f9ea1`; tinyexpr.h `6644032507c07816`; |
| p08_cjson | cJSON JSON parser | github.com/DaveGamble/cJSON | MIT (LICENSE) | cJSON.c `607e756460fa0de3`; cJSON.h `25b0145150d50049`; |
| p09_go | github.com/google/uuid v1.6.0 and github.com/spf13/pflag v1.0.5 (Go modules) | proxy.golang.org via go 1.24.7 | BSD-3-Clause both (licenses/uuid-LICENSE, licenses/pflag-LICENSE) | go.mod `843fcc61448a2410`; go.sum `1f2d44bbf7d249c7`; |

`p09_go` is built once, here, with `GOOS=darwin GOARCH=arm64 CGO_ENABLED=0 go build -buildvcs=false -trimpath -ldflags="-s -w"` (Go 1.24.7 on Linux x86_64) and shipped as `targets/prebuilt/p09_go`, so the Mac needs no Go install. `-buildvcs=false` keeps this repo's commit ID out of the binary.
