
import os
from packet import packet
from workspace_diff import line_diff, workspace_diff

class workspace:
    def __init__(self, data="skldfjsldaj"):
        self.__data = data

    def clone(self):
        """
        Clone the current workspace data, useful to do a diff
        :return:
        """
        w = workspace(self.__data)
        return w

    def apply_diff(self, diff):
        lines = self.__data.split('\n')
        offset = 0
        for ld in diff.lines_diff:
            if ld.diff_type == line_diff.LineChanged:
                lines[ld.line_id] = ld.line_data
            elif ld.diff_type == line_diff.LineAdded:
                lines.append(ld.line_data)
            elif ld.diff_type == line_diff.LineRemoved:
                if len(lines) > ld.line_id - offset:
                    lines.pop(ld.line_id - offset)
                    offset += 1

        data = ""
        for l in lines:
            data += "%s\n" % l

        data = data.rstrip('\n')

        self.__data = data



    def diff(self, new_workspace):
        diff = workspace_diff()

        lines = self.__data.split('\n')

        nw_lines = new_workspace.get_data().split('\n')

        ic = len(lines)
        nw_ic = len(nw_lines)

        i = 0

        while i < ic and i < nw_ic:
            cur_line = lines[i]
            new_line = nw_lines[i]

            if not cur_line == new_line:
                ld = line_diff(i, line_diff.LineChanged, new_line)
                diff.lines_diff.append(ld)
            i += 1

        if ic < nw_ic:
            while i < nw_ic:
                new_line = nw_lines[i]
                ld = line_diff(i, line_diff.LineAdded, new_line)
                diff.lines_diff.append(ld)
                i += 1
        elif ic > nw_ic:
            while i < ic:
                ld = line_diff(i, line_diff.LineRemoved)
                diff.lines_diff.append(ld)
                i += 1

        return diff

    def get_workspace_packet(self):
        """
        Generating a packet with all the text data
        :return:
        Forged packet
        """
        p = packet()
        p.packet_type = packet.Workspace
        p.fields['length'] = str(len(self.__data))
        p.fields['content'] = self.__data
        return p

    def flush(self):
        """
        Save tue current text data, depends on the implementation
        :return:
        """
        pass

    def insert(self, offset, text):
        if len(self.__data) > offset:
            self.__data = self.__data[0:offset] + text + self.__data[offset+1:]
        else:
            self.__data += text

    def append(self, text):
        self.__data += text

    def get_data(self):
        return self.__data

    def set_data(self, text):
        self.__data = text


class file_workspace(workspace):

    def __init__(self, file_path):
        workspace.__init__(self)
        self.file_path = file_path
        if file_path is not None:
            if os.path.exists(file_path):
                self.__load_file()
            else:
                #create a empty file
                self.__empty_file()

    def __empty_file(self):
        fp = open(self.file_path, 'w')
        fp.close()

    def __load_file(self):
        fp = open(self.file_path, 'r')
        text = ""

        line = fp.readline()

        while len(line) > 0:
            text += line
            line = fp.readline()

        if len(line) > 0:
            text += line

        fp.close()

        self.set_data(text)

    def flush(self):
        fp = open(self.file_path, 'w')
        fp.write(self.get_data())
        fp.close()


if __name__ == '__main__':
    print "Workspace Unit Test"

    fw = file_workspace('workspace .txt')
    #fw.__data = "allo"

    pack_str = fw.get_workspace_packet().to_string()
    print "Packet test"
    p = packet(pack_str)

    print p.to_string()

    #clone

    w2 = fw.clone()

    w2.insert(3, "aloooooo clone !!")

    print fw.get_data()
    print w2.get_data()

    _diff = fw.diff(w2)

    w3 = workspace()

    w3.set_data("bl balb daijfosdjfoisd kfosd kfsd")

    print _diff.to_string()
    _diff2 = fw.diff(w3)

    p = packet()

    _diff2.fill_packet(p)

    _diff3 = workspace_diff(p.fields['diff'])
    print _diff3.to_string()

    fw.apply_diff(_diff3)

    print w3.get_data()
    print "---------------"
    print fw.get_data()
