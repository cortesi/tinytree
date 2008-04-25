import os, os.path, cStringIO
import libpry
import tinytree

class u_isStringLike(libpry.AutoTree):
    def test_all(self):
        assert tinytree._isStringLike("foo")
        assert not tinytree._isStringLike([1, 2, 3])
        assert not tinytree._isStringLike((1, 2, 3))
        assert not tinytree._isStringLike(["1", "2", "3"])


class u_isSequenceLike(libpry.AutoTree):
    def test_all(self):
        assert tinytree._isSequenceLike([1, 2, 3])
        assert tinytree._isSequenceLike((1, 2, 3))
        assert not tinytree._isSequenceLike("foobar")
        assert tinytree._isSequenceLike(["foobar", "foo"])
        x = iter([1, 2, 3])
        assert tinytree._isSequenceLike(x)


class Node(tinytree.Tree):
    """
        Test helper class.
    """
    tprop = tinytree.Tree.treeProp("tprop")
    errprop = tinytree.Tree.treeProp("errprop")
    def __init__(self, name, children=None):
        tinytree.Tree.__init__(self, children)
        self.name = name
        self.lookup = {}

    def __getitem__(self, item):
        for i in self.children:
            if (i.name == item):
                return i
        else:
            raise KeyError

    def __eq__(self, name):
        """
            This won't stuff tinytree.Tree, as long as there is only ONE element with
            each title in the tree.
        """
        return (name == self.name)

    def __repr__(self):
        return "<%s>"%self.name

    stopper = False
    def adder(self, lst):
        lst.append(self.name)
        if self.stopper:
            return tinytree.STOP


class uTreeSimple(libpry.AutoTree):
    def setUp(self):
        self.node  = tinytree.Tree()
        self.nodeB = tinytree.Tree()

    def test_addChild(self):
        self.node.addChild(self.nodeB)
        assert self.nodeB.parent is self.node

    def test_count(self):
        assert self.nodeB.count() == 1

    def test_init_initialList(self):
        spec = [
            [ tinytree.Tree() ]
        ]
        libpry.raises(ValueError, tinytree.Tree, spec)

    def test_init_singleelement(self):
        spec = [ tinytree.Tree() ]
        t = tinytree.Tree(spec)
        assert len(t.children) == 1

    def test_init_doublelist_final(self):
        spec = [
            tinytree.Tree(),
            [ tinytree.Tree() ],
            [ tinytree.Tree() ]
        ]
        libpry.raises(ValueError, tinytree.Tree, spec)

    def test_init_doublelist_inner(self):
        spec = [
            tinytree.Tree(),
            [ tinytree.Tree() ],
            [ tinytree.Tree() ],
            tinytree.Tree(),
        ]
        libpry.raises(ValueError, tinytree.Tree, spec)

    def test_remove(self):
        nodes = [
            Node("one"),
            Node("two"),
            Node("three"),
        ]
        t = Node("root", nodes)
        n = t["two"]
        n.remove()
        assert len(t.children) == 2
        assert n.parent is None

        n = t["one"]
        n.remove()
        assert len(t.children) == 1

    def test_replace(self):
        nodes = [
            Node("one"),
            Node("two"),
            Node("three"),
        ]
        t = Node("root", nodes)
        n = t["two"]
        n.replace(Node("four"), Node("five"))
        assert len(t.children) == 4
        libpry.raises(KeyError, t.__getitem__, "two")

    def test_reparent(self):
        nodes = [
            Node("one"),
            Node("two"),
            Node("three"),
        ]
        t = Node("root", nodes)
        n = t["two"]
        node = n.reparent(Node("parent"))
        assert t["parent"]["two"]
        assert node.name == "parent"

    def test_clear(self):
        nodes = [
            Node("one"),
            Node("two"),
            Node("three"),
        ]
        t = Node("root", nodes)
        ret = t.clear()
        for i in ret:
            assert not i.parent
        assert not t.children

    def test_index(self):
        nodes = [
            Node("one"),
            Node("two"),
            Node("three"),
        ]
        t = Node("root", nodes)
        assert t["one"].index() == 0
        assert t["two"].index() == 1
        libpry.raises("node with no parent", t.index)

    def test_addChildrenFromList(self):
        nodes = [
            Node("one"),
            [
                Node("two"),
                Node("three"),
                    [
                        Node("four"),
                        Node("five"),
                    ]
            ],
            Node("six"),
        ]
        t = Node("root", nodes)
        assert len(t.children) == 2
        assert t.children[0].name == "one"
        one = t.children[0]
        assert len(one.children) == 2
        assert one.children[1].name == "three"
        three = one.children[1]
        assert len(three.children) == 2

    def test_addChildrenFromList_err(self):
        nodes = [
            Node("one"), [
                Node("two"),
            ], [
                Node("six"),
            ]
        ]
        libpry.raises("not a tree object", Node, "root", nodes)


class uconstructFromList(libpry.AutoTree):
    def test_foo(self):
        pages = [
            Node("one"),
            [
                Node("two"),
                Node("three"),
                    [
                        Node("four"),
                        Node("five"),
                    ]
            ],
            Node("six"),
        ]
        one = pages[0]
        six = pages[2]
        heads = tinytree.constructFromList(pages)
        assert one.count() == 5
        assert six.count() == 1
        assert len(heads) == 2

    def test_err(self):
        pages = [
            [ Node("one")]
        ]
        libpry.raises(ValueError, tinytree.constructFromList, pages)


class TopNode(Node):
    foo = "bar"
    tprop = "tprop"


class uTreeComposite(libpry.AutoTree):
    def setUp(self):
        self.lst = [
                TopNode("top"),
                [
                    Node("a"),
                    Node("b"),
                    Node("c"),
                    [
                        Node("ca"),
                        Node("cb")
                    ],
                    Node("d")
                ]
            ]
        self.tt = tinytree.constructFromList(self.lst)[0]

    def test_inject(self):
        n = Node("test")
        self.tt.inject(n)
        assert len(self.tt.children) == 1
        assert len(self.tt["test"].children) == 4

    def test_siblings(self):
        sibs = list(self.tt["a"].siblings())
        assert sibs == ["a", "b", "c", "d"]

    def test_siblings_root(self):
        sibs = list(self.tt.siblings())
        assert sibs == ["top"]

    def test_preOrder(self):
        assert list(self.tt.preOrder()) ==\
                ["top", "a", "b", "c", "ca", "cb", "d"]
        assert list(self.tt["a"].preOrder()) == ["a"]

    def test_postOrder(self):
        assert list(self.tt.postOrder()) ==\
                ["a", "b", "ca", "cb", "c", "d", "top"]
        assert list(self.tt["a"].postOrder()) == ["a"]

    def test_count(self):
        assert self.tt.count() == 7

    def test_pathToRoot(self):
        assert list(self.tt["c"]["ca"].pathToRoot()) == ["ca", "c", "top"]
        assert list(self.tt.pathToRoot()) == ["top"]
        assert list(self.tt["a"].pathToRoot()) == ["a", "top"]

    def test_pathFromRoot(self):
        assert list(self.tt["c"]["ca"].pathToRoot()) ==\
                list(reversed(list(self.tt["c"]["ca"].pathFromRoot())))

    def test_isDescendantOf(self):
        assert self.tt.isDescendantOf(self.tt["a"])
        assert self.tt["c"].isDescendantOf(self.tt["c"]["ca"])
        assert not self.tt["c"].isDescendantOf(self.tt["a"])
        assert not self.tt["c"].isDescendantOf(self.tt)

    def test_isSiblingOf(self):
        assert not self.tt.isSiblingOf(self.tt["a"])
        assert self.tt["a"].isSiblingOf(self.tt["b"])
        assert not self.tt["a"].isSiblingOf(self.tt["c"]["ca"])

    def test_getRoot(self):
        assert self.tt["c"]["ca"].getRoot() == self.tt
        assert self.tt["c"].getRoot() == self.tt
        assert self.tt.getRoot() == self.tt

    def test_findParent(self):
        def search(object):
            return 1
        assert self.tt["c"]["cb"].findParent(search) == self.tt["c"]
        def search(object):
            return (object.name == "top")
        assert self.tt["c"]["cb"].findParent(search) == self.tt

    def test_findForwards(self):
        def search(object):
            return 1
        assert self.tt["c"].findForwards(search) == self.tt["c"]["ca"]
        assert self.tt["d"].findForwards(search) == None
        assert self.tt["c"]["cb"].findForwards(search) == self.tt["d"]
        def search(object):
            return (object.name == "cb")
        assert self.tt.findForwards(search) == self.tt["c"]["cb"]
        assert self.tt["c"]["cb"].findForwards(search) == None

    def test_findForwardsMultiFunc(self):
        def s1(object):
            return 1
        def s2(object):
            return (object.name == "cb")
        assert self.tt.findForwards(s1, s2).name == "cb"
        def s1(object):
            return 0
        assert self.tt.findForwards(s1, s2) == None

    def test_findForwardsKey(self):
        assert self.tt.findForwards(name="cb").name == "cb"
        assert self.tt.findForwards(name="nonexistent") == None
        assert self.tt.findForwards(name="cb", children=[]).name == "cb"
        assert self.tt.findForwards(name="cb", children="foo") == None
        assert self.tt.findForwards(porky="cb") == None

    def test_findForwardsCombo(self):
        def s1(object):
            return (object.name == "cb")
        assert self.tt.findForwards(s1, name="c") == None
        assert self.tt.findForwards(s1, name="cb").name == "cb"

    def test_findChild(self):
        def search(object):
            return (object.name == "cb")
        assert self.tt.findChild(search).name == "cb"
        assert self.tt["c"].findChild(search).name == "cb"
        assert self.tt["a"].findChild(search) is None

    def test_findBackwards(self):
        def search(object):
            return 1
        assert self.tt["c"]["ca"].findBackwards(search) == self.tt["c"]
        assert self.tt.findBackwards(search) == None
        assert self.tt["c"]["cb"].findBackwards(search) == self.tt["c"]["ca"]
        def search(object):
            return (object.name == "cb")
        assert self.tt["d"].findBackwards(search) == self.tt["c"]["cb"]
        assert self.tt["c"]["cb"].findBackwards(search) == None

    def test_getPrevious(self):
        assert self.tt["a"].getPrevious() == self.tt
        assert self.tt["c"].getPrevious() == self.tt["b"]
        assert self.tt["c"]["ca"].getPrevious() == self.tt["c"]
        assert self.tt.getPrevious() == None

    def test_getNext(self):
        assert self.tt["c"].getNext() == self.tt["c"]["ca"]
        assert self.tt["a"].getNext() == self.tt["b"]
        assert self.tt["c"]["cb"].getNext() == self.tt["d"]
        assert self.tt["d"].getNext() == None

    def test_getDepth(self):
        assert self.tt.getDepth() == 1
        assert self.tt["c"].getDepth() == 2
        assert self.tt["c"]["cb"].getDepth() == 3

    def test_findAttr(self):
        assert self.tt["c"]["cb"].findAttr("foo") == "bar"
        assert self.tt.findAttr("foo") == "bar"
        assert self.tt.findAttr("wibble", "bar") == "bar"
        assert not self.tt["c"]["cb"].findAttr("nonexistent")

    def test_attrsFromRoot(self):
        x = list(self.tt["c"].attrsToRoot("nonexistent"))
        assert x == []
        x = list(self.tt["c"]["cb"].attrsToRoot("foo"))
        assert x == ["bar"]
        self.tt["c"].foo = "one"
        x = list(self.tt["c"]["cb"].attrsToRoot("foo"))
        assert x == ["one", "bar"]

    def test_treeProp(self):
        assert self.tt["c"]["cb"].tprop == "tprop"
        self.tt["c"].tprop = "cprop"
        assert self.tt["c"]["cb"].tprop == "cprop"

    def test_treeProp_notdefined(self):
        libpry.raises(
            "errprop not defined",
            getattr, self.tt["c"]["cb"],
            "errprop"
        )

    def test_dump(self):
        cs = cStringIO.StringIO()
        self.tt.dump(cs)


tests = [
    u_isStringLike(),
    u_isSequenceLike(),
    uTreeSimple(),
    uconstructFromList(),
    uTreeComposite()
]
