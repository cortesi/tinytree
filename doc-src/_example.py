import tinytree

class T(tinytree.Tree):
    def __init__(self, name, children=None):
        tinytree.Tree.__init__(self, children)
        self.name = name

    def __repr__(self):
        return "<%s>"%self.name


n = T(
        "root",
        [T("one"), T("two"), [ T("three") ], T("four") ]
    )
n.dump()
print list(n.preOrder())
print list(n.postOrder())
print n.findForwards(name="three")
