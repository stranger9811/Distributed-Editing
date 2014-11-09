'''
 Cours : LOG735
 Session : Ete 2014
 Groupe : 01
 Projet : editeur de texte distribue
 Etudiants :
    Jordan Guerin
    Frederic Langlois
 Code(s) perm. :
    GUEJ06118807
    LANF07078402
 ==================================================================
 Description of file

 permet de faire la difference entre deux workspace pour savoir ce qui a ete modifie, inserer et supprimer
 ==================================================================
'''
import re


class line_diff:
    (LineAdded, LineChanged, LineRemoved) = (0, 1, 2)

    def __init__(self, line_id=-1, diff_type=LineChanged, line_data=""):
        self.diff_type = diff_type
        self.line_id = line_id
        self.line_data = line_data

    def from_string(self, data):
        pattern = re.compile("i=(?P<line_id>[0-9]+) type=(?P<type>[0-9]+) data=(?P<data>.*)")

        m = pattern.match(data)

        if m:
            self.line_id = int(m.group("line_id"))
            self.diff_type = int(m.group("type"))
            self.line_data = m.group("data")
        else:
            #todo exception maybe
            print "line_diff parsing error [%s]" % data

    def to_string(self):
        return "i=%d type=%d data=%s" % (self.line_id, self.diff_type, self.line_data)

class workspace_diff:
    (LineDiffSeparator) = '--L_D--'

    def __init__(self, text_data=None):
        self.lines_diff = []

        if text_data is not None:
            self.__from_string(text_data)

    def __from_string(self, text_data):
        diffs = text_data.split(self.LineDiffSeparator)

        for d in diffs:
            if len(d) > 0:
                ld = line_diff()
                ld.from_string(d)
                self.lines_diff.append(ld)

    def is_empty(self):
        return len(self.lines_diff) == 0

    def to_string(self):
        txt = "workspace_diff:\n"
        for d in self.lines_diff:
            txt += "\ttype: %d, line_id: %d, data: %s\n" % (d.diff_type, d.line_id, d.line_data)

        return txt

    def fill_packet(self, packet):
        data = ""

        for ld in self.lines_diff:
            data += "%s%s" % (ld.to_string(), self.LineDiffSeparator)

        packet.fields['diff'] = data

        return packet