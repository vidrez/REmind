import r2pipe
import json
from base64 import b64decode
import sys

output_path = ''
d = dict()
angr_offset = int('0x400000', 16)  # NOTE! Change it if using PIE

if __name__ == '__main__':
    filename = sys.argv[1]
    output_path = sys.argv[2] + '/'

    f = open(output_path + 'offset.json', 'r')
    d = json.loads(f.readlines()[0])

    debugged = r2pipe.open(filename)
    debugged.cmd('aaa')
    strings = json.loads(debugged.cmd('izj'))

    string_dict = dict()

    for line in strings:
        vaddr = hex(int(line['vaddr']))

        # normalizza indirizzo
        i = 0
        c = vaddr[i]
        while c == '0' or c == 'x':
            i += 1
            c = vaddr[i]

        print("vaddr->" + vaddr[i:])

        xrefs_to_string = debugged.cmd('axtj@' + "0x" + vaddr[i:])
        xref_dict_raw = json.loads(xrefs_to_string[:-1])
        xref_list = []
        addr_list = []
        opcode_list = []

        print(xref_dict_raw)

        # processa xrefs
        for xref in xref_dict_raw:
            print(xref)
            if 'fcn_name' in xref:
                ret = xref['fcn_addr']
                if ret != "":
                    addr_list.append(hex(xref['from'] + angr_offset))
                    func_addr = hex(ret + angr_offset)
                    my_function_name = 'sub_{0}'.format(func_addr[2:])
                    xref_list.append(my_function_name)
                    opcode_list.append(xref['opcode'])

        print(xref_list)

        xref_dict = {"xref": xref_list}
        addr_dict = {"addr": addr_list}
        opcode_dict = {"opcode": opcode_list}

        # FIX robusto per decode base64
        try:
            value = b64decode(line['string']).decode('utf-8')
        except Exception:
            value = line['string']

        val_dict = {"str": value}

        # salva solo stringhe usate
        if len(xref_list) >= 1:
            string_dict[vaddr] = [xref_dict, val_dict, addr_dict, opcode_dict]

    print(string_dict)

    # salva strings.json
    with open(output_path + 'strings.json', 'w') as strings_fd:
        strings_fd.write(json.dumps(string_dict))

    # salva info.json
    info = json.loads(debugged.cmd('ij'))
    info_dict = info["core"]
    for key in info["bin"]:
        info_dict[key] = info["bin"][key]

    open(output_path + 'info.json', 'w').write(json.dumps(info_dict))
