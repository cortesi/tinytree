import pylid, os, os.path, cStringIO
import tinytree

class u_isStringLike(pylid.TestCase):
    def test_all(self):
        self.failUnless(tinytree._isStringLike("foo"))
        self.failIf(tinytree._isStringLike([1, 2, 3]))
        self.failIf(tinytree._isStringLike((1, 2, 3)))
        self.failIf(tinytree._isStringLike(["1", "2", "3"]))


class u_isSequenceLike(pylid.TestCase):
    def test_all(self):
        self.failUnless(tinytree._isSequenceLike([1, 2, 3]))
        self.failUnless(tinytree._isSequenceLike((1, 2, 3)))
        self.failIf(tinytree._isSequenceLike("foobar"))
        self.failUnless(tinytree._isSequenceLike(["foobar", "foo"]))
        x = iter([1, 2, 3])
        self.failUnless(tinytree._isSequenceLike(x))


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


class uTreeSimple(pylid.TestCase):
    def setUp(self):
        self.node  = tinytree.Tree()
        self.nodeB = tinytree.Tree()

    def test_addChild(self):
        self.node.addChild(self.nodeB)
        self.failUnless(self.nodeB.parent is self.node)

    def test_nodeCount(self):
        self.failUnless(self.nodeB.nodeCount() == 1)

    def test_init_initialList(self):
        spec = [
            [ tinytree.Tree() ]
        ]
        self.assertRaises(ValueError, tinytree.Tree, spec)

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
        self.assertRaises(ValueError, tinytree.Tree, spec)

    def test_init_doublelist_inner(self):
        spec = [
            tinytree.Tree(),
            [ tinytree.Tree() ],
            [ tinytree.Tree() ],
            tinytree.Tree(),
        ]
        self.assertRaises(ValueError, tinytree.Tree, spec)

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
        self.failWith("not a tree object", Node, "root", nodes)


class uconstructFromList(pylid.TestCase):
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
        self.failUnlessEqual(one.nodeCount(), 5)
        self.failUnlessEqual(six.nodeCount(), 1)
        self.failUnlessEqual(len(heads), 2)

    def test_err(self):
        pages = [
            [ Node("one")]
        ]
        self.failUnlessRaises(ValueError, tinytree.constructFromList, pages)


class TopNode(Node):
    foo = "bar"
    tprop = "tprop"


class uTreeComposite(pylid.TestCase):
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

    def test_double(self):
        tt = tinytree.constructFromList(self.lst)[0]
        x1 = len(list(tt.preOrder()))
        tt = tinytree.constructFromList(self.lst)[0]
        x2 = len(list(tt.preOrder()))
        self.failUnlessEqual(x1, x2)

    def test_siblings(self):
        sibs = list(self.tt["a"].siblings())
        self.failUnlessEqual(sibs, ["a", "b", "c", "d"])

    def test_siblings_root(self):
        sibs = list(self.tt.siblings())
        self.failUnlessEqual(sibs, ["top"])

    def test_preOrder(self):
        self.failUnlessEqual(list(self.tt.preOrder()), [
                                "top",
                                "a",
                                "b",
                                "c",
                                "ca",
                                "cb",
                                "d",
                                ])
        self.failUnlessEqual(list(self.tt["a"].preOrder()), ["a"])

    def test_postOrder(self):
        self.failUnlessEqual(list(self.tt.postOrder()), [
                                "a",
                                "b",
                                "ca",
                                "cb",
                                "c",
                                "d",
                                "top"
                                ])
        self.failUnlessEqual(list(self.tt["a"].postOrder()), ["a"])

    def test_nodeCount(self):
        self.failUnlessEqual(self.tt.nodeCount(), 7)

    def test_pathToRoot(self):
        self.failUnlessEqual(list(self.tt["c"]["ca"].pathToRoot()), ["ca", "c", "top"])
        self.failUnlessEqual(list(self.tt.pathToRoot()), ["top"])
        self.failUnlessEqual(list(self.tt["a"].pathToRoot()), ["a", "top"])

    def test_isDescendantOf(self):
        self.failUnless(self.tt["a"].isDescendantOf(self.tt))
        self.failUnless(self.tt["c"]["ca"].isDescendantOf(self.tt["c"]))
        self.failIf(self.tt["a"].isDescendantOf(self.tt["c"]))
        self.failIf(self.tt.isDescendantOf(self.tt["c"]))

    def test_getTopNode(self):
        self.failUnlessEqual(self.tt["c"]["ca"].getTopNode(), self.tt)
        self.failUnlessEqual(self.tt["c"].getTopNode(), self.tt)
        self.failUnlessEqual(self.tt.getTopNode(), self.tt)

    def test_getLast(self):
        self.failUnlessEqual(self.tt.getLast(), self.tt["d"])
        self.failUnlessEqual(self.tt["c"].getLast(), self.tt["c"]["cb"])
        self.failUnlessEqual(self.tt["a"].getLast(), self.tt["a"])

    def test_getFirst(self):
        self.failUnlessEqual(self.tt.getFirst(), self.tt["a"])
        self.failUnlessEqual(self.tt["c"].getFirst(), self.tt["c"]["ca"])
        self.failUnlessEqual(self.tt["a"].getFirst(), self.tt["a"])

    def test_findForwards(self):
        def search(object):
            return 1
        self.failUnlessEqual(self.tt["c"].findForwards(search), self.tt["c"]["ca"])
        self.failUnlessEqual(self.tt["d"].findForwards(search), None)
        self.failUnlessEqual(self.tt["c"]["cb"].findForwards(search), self.tt["d"])
        def search(object):
            return (object.name == "cb")
        self.failUnlessEqual(self.tt.findForwards(search), self.tt["c"]["cb"])
        self.failUnlessEqual(self.tt["c"]["cb"].findForwards(search), None)

    def test_findBackwards(self):
        def search(object):
            return 1
        self.failUnlessEqual(self.tt["c"]["ca"].findBackwards(search), self.tt["c"])
        self.failUnlessEqual(self.tt.findBackwards(search), None)
        self.failUnlessEqual(self.tt["c"]["cb"].findBackwards(search), self.tt["c"]["ca"])
        def search(object):
            return (object.name == "cb")
        self.failUnlessEqual(self.tt["d"].findBackwards(search), self.tt["c"]["cb"])
        self.failUnlessEqual(self.tt["c"]["cb"].findBackwards(search), None)

    def test_getPrevious(self):
        self.failUnlessEqual(self.tt["a"].getPrevious(), self.tt)
        self.failUnlessEqual(self.tt["c"].getPrevious(), self.tt["b"])
        self.failUnlessEqual(self.tt["c"]["ca"].getPrevious(), self.tt["c"])
        self.failUnlessEqual(self.tt.getPrevious(), None)

    def test_getNext(self):
        self.failUnlessEqual(self.tt["c"].getNext(), self.tt["c"]["ca"])
        self.failUnlessEqual(self.tt["a"].getNext(), self.tt["b"])
        self.failUnlessEqual(self.tt["c"]["cb"].getNext(), self.tt["d"])
        self.failUnlessEqual(self.tt["d"].getNext(), None)

    def test_getDepth(self):
        self.failUnlessEqual(self.tt.getDepth(), 1)
        self.failUnlessEqual(self.tt["c"].getDepth(), 2)
        self.failUnlessEqual(self.tt["c"]["cb"].getDepth(), 3)

    def test_findAttr(self):
        self.failUnlessEqual(self.tt["c"]["cb"].findAttr("foo"), "bar")
        self.failUnlessEqual(self.tt.findAttr("foo"), "bar")
        self.failUnlessEqual(self.tt.findAttr("wibble", "bar"), "bar")
        self.failIf(self.tt["c"]["cb"].findAttr("nonexistent"))

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
        self.failWith(
            "errprop not defined",
            getattr, self.tt["c"]["cb"],
            "errprop"
        )

    def test_getNamespaceKey(self):
        self.tt.ns = dict(a=1)
        n = self.tt["c"]["cb"]
        assert list(n.getNamespaceKey("ns", "a")) == [1]
        assert list(n.getNamespaceKey("ns", "b")) == []
        self.tt["c"].ns = dict(a=2)
        assert list(n.getNamespaceKey("ns", "a")) == [2, 1]

    def test_dump(self):
        cs = cStringIO.StringIO()
        self.tt.dump(cs)
