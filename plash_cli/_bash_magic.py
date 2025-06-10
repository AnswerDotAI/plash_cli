from IPython.core.magic import register_line_cell_magic
from bash_kernel.kernel import BashKernel
import re
from pathlib import Path

bk = BashKernel()
ip = get_ipython()

def interpolate_variables(text):
    """Find all $`varname` patterns and interpolate from IPython namespace"""
    for match in re.finditer(r'\$`([^`]+)`', text):
        varname = match.group(1)
        if varname not in ip.user_ns:
            raise NameError(f"Variable '{varname}' not found in IPython namespace")
        text = text.replace(match.group(0), str(ip.user_ns[varname]))
    return text

@register_line_cell_magic
def bash(line, cell=None): 
    code = f'{line}\n{cell}' if cell else line
    code = interpolate_variables(code)
    print(bk.bashwrapper.run_command(code))

@register_line_cell_magic
def writefile(line, cell):
    cell = interpolate_variables(cell)
    pwd = bk.bashwrapper.run_command('pwd').strip()
    fpath = Path(pwd) / line
    fpath.write_text(cell)
