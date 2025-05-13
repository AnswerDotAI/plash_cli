from IPython.core.magic import register_line_cell_magic
from bash_kernel.kernel import BashKernel
from functools import partial
import re
from pathlib import Path

bk = BashKernel()
ip = get_ipython()

@register_line_cell_magic
def bash(line, cell=None): 
    code = f'{line}\n{cell}' if cell else line
    # Get IPython shell instance
    
    # Find all $`varname` patterns and interpolate from IPython namespace
    for match in re.finditer(r'\$`([^`]+)`', code):
        varname = match.group(1)
        if varname not in ip.user_ns:
            raise NameError(f"Variable '{varname}' not found in IPython namespace")
        code = code.replace(match.group(0), str(ip.user_ns[varname]))
    print(bk.bashwrapper.run_command(code))

@register_line_cell_magic
def writefile(line, cell):
    pwd = bk.bashwrapper.run_command('pwd').strip()
    fpath = Path(pwd) / line
    fpath.write_text(cell)
