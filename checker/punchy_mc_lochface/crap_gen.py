import random
import os
import string
from jinja2 import Template

def gen_crap():
    tests = ['add', 'sql', 'fortran', 'nop']
    random.shuffle(tests)
    check_file = tests[0]
    print('chosen:' + check_file)

    if check_file == 'add':
        with open(os.path.join(os.path.dirname(__file__),'add.cob')) as f:
            add_template = Template(f.read())
            names = list(string.ascii_uppercase)
            random.shuffle(names)
            var1 = names[0] + names[1] + '1'
            var2 = names[2] + names[3] + '1'
            name = names[4] + names[5] + '1'
            val1 = random.randrange(0, 90)
            val2 = random.randrange(0, 90)
            res = val1 + val2
            return add_template.render(var1=var1, var2=var2, val1=val1, val2=val2, name=name), str(res).zfill(4)
    elif check_file == 'sql':
        with open(os.path.join(os.path.dirname(__file__),'sql.cob')) as f:
            return f.read(), 'Error.'
    elif check_file == 'fortran':
        with open(os.path.join(os.path.dirname(__file__),'fortran.cob')) as f:
            return f.read(), 'Error.'
    elif check_file == 'nop':
        with open(os.path.join(os.path.dirname(__file__),'nop.cob')) as f:
            return f.read(), 'Error.'
