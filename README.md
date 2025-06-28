# MultiagentLogic



### ！Important: PROVER9 Path Configuration

You need to configure the PROVER9 path based on your operating system in `src/symbolic_solvers/fol_solver/prover9_solver.py` (around line 20-21).

#### For Different Operating Systems:

**Linux Users:**
```python
os.environ['PROVER9'] = PROVER9_PATH  # 直接复用原repo prover9
```

**macOS Users:**
```python
os.environ['PROVER9'] = '/opt/homebrew/bin'  # macOS version installed via Homebrew
```
macOS users should install Prover9 via Homebrew and use this configuration. To install Prover9 on macOS:
```bash
brew install prover9
```

**Windows Users:**
Sorry不太熟悉windowsOS, same 安装PROVER9并配置路径即可