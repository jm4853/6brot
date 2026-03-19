# [v/u/p] <a+bi> <a+bi> <a+bi>
# [v/u/p][z/c/a] <a+bi>
# [v/u/p][z/c/a][r/i] <a>
# ex:
#   p 1.0+3.0i 0.0+1.0i 1.0+0.0i
#   ua 3.2+2.0i
#   vzi 5.3
#
# Interpreter will echo the command on success, and do nothing on failure

class Parser:
    def __init__(self, vecs=None):
        if vecs is None:
            vecs = dict()
        self.vecs = vecs
    def parse_line(self, line):
        if not line[0].lower() in self.vecs.keys():
            return ''
        vec_c = line[0].lower()
        if not (val_c := line[1].lower()) in self.vecs[vec_c].keys():
            val = self.parse_three_complex(line[1:].strip())
            if not val:
                return ''
            self.vecs[vec_c] = val
            val_str = ', '.join([f'{z[0]}+{z[1]}i' for z in val])
            return f'> {vec_c} = {val_str}\n'
        if not line[2].lower() in self.vecs[vec_c][val_c].keys():
            val = self.parse_complex(line[2:].strip())
            if not val:
                return ''
            self.vecs[vec_c][val_c] = val
            return f'> {vec_c}[{val_c}] = {val[0]}+{val[1]}i\n'
        r_c = line[2].lower()
        val = self.parse_real(line[3:])
        if not val:
            return ''
        self.vecs[vec_c][val_c][r_c] = val
        return f'> {vec_c}[{val_c}][{r_c}] = {val}\n'
    def _parse_n_complex(self, line, n):
        vs = []
        for seg in line.split(','):
            v = self.parse_complex(seg)
            if not v:
                return None
            vs.append(seg)
        if len(vs) != n:
            return None
        return vs
    def parse_three_complex(self, line):
        return self._parse_n_complex(line, 3)
    def parse_complex(self, line):
        segs = line.split('+')
        if len(segs) != 2:
            return None
        try:
            a = float(segs[0])
        except ValueError:
            return None
        if 'i' in segs[1]:
            segs = segs[1].split('i')[0]
        try:
            b = float(segs)
        except ValueError:
            return None
        return (a, b)
    def parse_real(self, line):
        try:
            a = float(line)
        except ValueError:
            return None
        return a


class VectorInterpreter:
    def __init__(self):
        self.vecs = dict()
        for k1 in ['v', 'u', 'p']:
            self.vecs[k1] = dict()
            for k2 in ['z', 'c', 'a']:
                self.vecs[k1][k2] = dict()
                self.vecs[k1][k2] = dict()
                for k3 in ['r', 'i']:
                    self.vecs[k1][k2][k3] = 0.0
        self.p = Parser(self.vecs)

    def run(self):
        while True:
            line = input()
            print(self.p.parse_line(line.strip()), end='')


