# Suggestion: Enhanced Port System for EonApiEditor

## Problem Statement
The current system uses "Primary IO + Side IO" ports and refers to "PIPEs". This is less intuitive than a system where ports are explicitly named and numbered, and where inputs/outputs have independent indexing.

## Proposed Solution: Numbered & Named Ports

### 1. Data Structure Update
Define ports as distinct entities with semantic names.
- **Input Port**: `(Index, Name, Type)`
- **Output Port**: `(Index, Name, Type)`

Independent indexing:
- `Input[0]`, `Input[1]`, ...
- `Output[0]`, `Output[1]`, ...

### 2. EonApiEditor UI Enhancements
- **Port Manager**: A dedicated sidebar or tab to define ports.
- **Inline Naming**: Allow renaming ports directly on the block diagram.
- **Visual Distinction**: Use different colors or shapes to distinguish between primary flow ports and auxiliary side ports, even if they all follow the same numbering scheme.

### 3. Transition from "PIPEs"
- Rename "PIPE" references to "Connections" or "Signals".
- Map existing "Primary" to `Index 0` and "Side" to `Index 1+`.
- Store the user-defined names in the `.eon` file metadata or within the port definition block.

### 4. Example Transformation
**Old:**
- Primary Input
- Side Input 1
- Pipe 0

**New:**
- Input[0]: "MainRequest"
- Input[1]: "ConfigData"
- Connection: "RequestFlow"
