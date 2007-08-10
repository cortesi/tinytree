import sys, itertools, copy

def _isStringLike(anobj):
    try:
        # Avoid succeeding expensively if anobj is large.
        anobj[:0]+''
    except:
        return 0
    else:
        return 1


def _isSequenceLike(anobj):
    if not hasattr(anobj, "next"):
        if _isStringLike(anobj):
            return 0
        try:
            anobj[:0]
        except:
            return 0
    return 1


class Visitor:
    pass


class Tree(object):
    """
        A simple implementation of an ordered tree. 
    """
    def __init__(self, children = None):
        """
            Argument is a nested list specifying a tree of children.
        """
        self.children = []
        if children:
            self.addChildrenFromList(children)
        self.parent = None
            
    def addChildrenFromList(self, children):
        skip = True
        v = zip(
            itertools.chain([None], children),
            itertools.chain(children, [None])
        )
        for i in v:
            if skip:
                skip = False
                continue
            self.addChild(i[0])
            if _isSequenceLike(i[1]):
                i[0].addChildrenFromList(i[1])
                skip = True

    def addChild(self, node):
        """
            Add a child to this node. The node object MUST obey the Pytree
            interface.
        """
        if not isinstance(node, Tree):
            s = "Invalid tree specification: %s is not a Tree object."%repr(node)
            raise ValueError(s)
        if not node in self.children:
            node.parent = self
            self.children.append(node)

    def isDescendantOf(self, obj):
        """
            Returns true if object lies somewhere on the path to the root. 
        """
        return (obj in self.pathToRoot())

    def siblings(self):
        """
            Generator yielding all siblings of this object, including this
            object itself.

        """
        if not self.parent:
            yield self
        else:
            for i in self.parent.children:
                yield i

    def pathToRoot(self):
        """
            Generator yielding all objects on the path from this element to the
            root of the tree, including ourselves.
        """
        itm = self
        while 1:
            yield itm
            if itm.parent:
                itm = itm.parent
            else:
                break

    def getTopNode(self):
        """
            Return the topmost node in the tree.
        """
        for i in self.pathToRoot():
            pass
        return i

    def preOrder(self):
        """
            Return a list of the elements of the tree in PreOrder.
        """
        yield self
        for i in self.children:
            for j in i.preOrder():
                yield j

    def postOrder(self):
        """
            Return a list of the elements of the tree in PreOrder.
        """
        for i in self.children:
            for j in i.postOrder():
                yield j
        yield self

    def getLast(self):
        """
            Get the last item in the subtree. 

            Here "last" is defined as the last item in the preOrder traversal
            of the tree.
        """
        for i in self.preOrder():
            pass
        return i

    def getFirst(self):
        """
            Get the first item in the subtree.
            
            Here, "first" is defined as the first item in the postOrder
            traversal of the tree.
        """
        return self.postOrder().next()

    def findForwards(self, func):
        """
            Search the preOrder tree forwards, passing each element to func,
            until func returns true, then return the matched object. Return
            None if object not found.

            preOrder was chosen as the most useful order, since it matches the
            natural "previous" and "next" order of a document. 
        """
        itr = self.getTopNode().preOrder()
        for i in itr:
            if i == self:
                break
        for i in itr:
            if func(i):
                return i
        return None

    def findBackwards(self, func):
        """
            Search the preOrder tree backwards, passing each element to func,
            until func returns true, then return the matched object. Return
            None if object not found.

            preOrder was chosen as the most useful order, since it matches the
            natural "previous" and "next" order of a document. 
        """
        # FIXME: Dreadfully inefficient...
        lst = list(self.getTopNode().preOrder())
        lst.reverse()
        myIndex = lst.index(self)
        for i in lst[(myIndex+1):]:
            if func(i):
                return i
        return None

    def getPrevious(self):
        """
            Find the previous node in the preOrder listing of the tree. 
        """
        return self.findBackwards(lambda x: 1)

    def getNext(self):
        """
            Find the next node in the preOrder listing of the tree. 
        """
        return self.findForwards(lambda x: 1)

    def nodeCount(self):
        """
            Number of nodes in this tree, including the root.
        """
        return len(list(self.preOrder()))

    def getDepth(self):
        """
            Return the depth of this node.
        """
        return len(list(self.pathToRoot()))

    def findAttr(self, attr, default=None):
        """
            Traverses the path to the root of the tree, looking for the
            specified attribute. If it is found, return it, else return None.
        """
        for i in self.pathToRoot():
            if hasattr(i, attr):
                return getattr(i, attr)
        return default

    def attrsToRoot(self, attr):
        """
            Traverses the path from this node to the root of the tree, and
            yields a value for each attribute. Nodes that do not have the
            attribute and attribute values that test false are ignored.
        """
        lst = []
        for i in self.pathToRoot():
            v = getattr(i, attr, None)
            if v:
                yield v

    def getNamespaceKey(self, attr, key):
        """
            A namespace is a dictionary-like attribute on a node. This
            generator yield the key "key" from all attributes named "attr"
            between this node and the root.
        """
        for i in self.attrsToRoot(attr):
            n = i.get(key, None)
            if n:
                yield n

    @staticmethod
    def treeProp(name):
        def fget(self):
            if self.__dict__.has_key(name):
                return self.__dict__[name]
            else:
                if not self.parent:
                    raise ValueError, "Property %s not defined."%name
                return getattr(self.parent, name)
        def fset(self, value):
            self.__dict__[name] = value
        return property(fget, fset)

    def dump(self, outf=sys.stdout):
        for i in self.preOrder():
            print >> outf, "\t"*(i.getDepth()-1), i


def constructFromList(lst):
    """
        Takes a nested list of Tree objects, and creates the link structure to
        turn it into a forest of trees.

        Returns a list consisting of the nodes at the base of each tree.  Lists
        are constructed "bottom-up", so all parent nodes for a particular node
        are guaranteed to exist when "addChild" is run.
    """
    heads = []
    for i, val in enumerate(lst):
        if _isSequenceLike(val):
            if i == 0 or _isSequenceLike(lst[i-1]):
                raise ValueError, "constructFromList: Invalid list."
            lst[i-1].addChildrenFromList(val)
        else:
            heads.append(val)
    return heads
