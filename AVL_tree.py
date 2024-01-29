"""
Based on the code provided at: https://github.com/laurentluce/python-algorithms/blob/master/algorithms/binary_tree.py
Extended to AVL trees by Karl Southern
"""
from tkinter import Tk, Canvas
from enum import Enum, auto as enum_auto


class RestructuringCase(Enum):
    Balanced = enum_auto()
    LeftLeft = enum_auto()
    LeftRight = enum_auto()
    RightLeft = enum_auto()
    RightRight = enum_auto()

    @classmethod
    def determine_case(cls, x, y, z):
        """
        Takes three nodes such that x.parent = y, y.parent = z and returns the 'restructuring' case that is exhibited

        :param x: Bottommost node
        :param y: Middle node
        :param z: Topmost node
        :return: exhibited RestructuringCase
        """
        if not z.unbalanced():
            return cls.Balanced

        if z.left == y:
            if y.left == x:
                return cls.LeftLeft
            else:
                return cls.LeftRight
        else:
            if y.right == x:
                return cls.RightRight
            else:
                return cls.RightLeft


class Node:
    """
    Tree node: left and right child + data which can be any object
    """

    def __init__(self, data):
        """
        Node constructor

        :param data: node data object
        """
        self.left = None
        self.right = None
        self.data = data
        self.parent = None

    def lookup(self, data):
        """
        Lookup node containing data

        :param data: node data object to look up
        :returns: node if found
        :raise ValueError: data is not in tree
        """
        if data < self.data:
            if self.left is None:
                raise ValueError(f"{data} is not in tree")

            return self.left.lookup(data)

        if data > self.data:
            if self.right is None:
                raise ValueError(f"{data} is not in tree")

            return self.right.lookup(data)

        return self

    def __replace_with_node(self, with_node):
        """
        Replace this node's data and descendants with attributes from another node

        :param with_node: the node to take attributes from
        """
        self.__replace(with_node.data, with_node.left, with_node.right)

    def __replace(self, data, left, right):
        """
        Replace this node's data and descendants

        :param data: the new node data
        :param left: the new 'left' node
        :param right: the new 'right' node
        """
        self.left = left
        if self.left is not None:
            self.left.parent = self

        self.right = right
        if self.right is not None:
            self.right.parent = self

        self.data = data

    def refresh_parents(self):
        """
        Refresh the parents of all descendant nodes
        """
        if self.left is not None:
            self.left.parent = self
            self.left.refresh_parents()

        if self.right is not None:
            self.right.parent = self
            self.right.refresh_parents()

    def __no_children_delete(self):
        """
        Remove this node from the tree, assuming it has no children
        """
        # just remove it
        if not self.parent:
            del self
            return

        if self.parent.left is self:
            self.parent.left = None
        else:
            self.parent.right = None
        del self

    def __one_child_delete(self):
        """
        Remove this node from the tree, assuming it has exactly one child
        """
        # replace node with its child
        child = self.left or self.right
        self.__replace_with_node(child)

    def __two_children_delete(self):
        """
        Remove this node from the tree, assuming it has exactly two children
        """
        # find its successor: once to the right, then all the way left
        successor = self.right
        while successor.left is not None:
            successor = successor.left
        # replace node data by its successor data
        self.data = successor.data
        # fix successor's parent's child
        if successor.parent is self:
            self.right = successor.right
            if self.right:
                self.right.parent = self
            return

        successor.parent.left = successor.right
        if successor.parent.left:
            successor.parent.left.parent = successor.right

    def delete(self, data):
        """
        Delete node containing data

        :param data: node's content to delete
        :raise ValueError: data is not in tree
        """
        # get node containing data
        node = self.lookup(data)
        if node is None:
            raise ValueError("data is not in tree")

        children_count = node.children_count()
        if children_count == 0:
            node.__no_children_delete()
            return

        if children_count == 1:
            node.__one_child_delete()
            return

        node.__two_children_delete()

    def children_count(self):
        """
        Returns the number of children a node has

        :returns: number of children: 0, 1, 2
        """
        return int(self.left is not None) + int(self.right is not None)

    @classmethod
    def pre_order_traverse(cls, node):
        """
        Traverse a node's (sub)tree in pre-order

        :param node: the node whose (sub)tree you wish to traverse
        :return: an iterator that traverses the (sub)tree
        """
        yield node.data
        if node.left is not None:
            yield from cls.pre_order_traverse(node.left)
        if node.right is not None:
            yield from cls.pre_order_traverse(node.right)

    @classmethod
    def in_order_traverse(cls, node):
        """
        Traverse a node's (sub)tree in-order

        :param node: the node whose (sub)tree you wish to traverse
        :return: an iterator that traverses the (sub)tree
        """
        if node.left is not None:
            yield from cls.in_order_traverse(node.left)
        yield node.data
        if node.right is not None:
            yield from cls.in_order_traverse(node.right)

    @classmethod
    def post_order_traverse(cls, node):
        """
        Traverse a node's (sub)tree in post-order

        :param node: the node whose (sub)tree you wish to traverse
        :return: an iterator that traverses the (sub)tree
        """
        if node.left is not None:
            yield from cls.post_order_traverse(node.left)
        if node.right is not None:
            yield from cls.post_order_traverse(node.right)
        yield node.data

    def print_tree(self):
        """
        Print tree content inorder
        """
        data = list(self.in_order_traverse(self))
        print(data)

    def count_levels(self):
        """
        Count the number of levels in the tree
        """
        if (self.left is None) and (self.right is None):
            return 1

        if self.left is None:
            return self.right.count_levels() + 1

        if self.right is None:
            return self.left.count_levels() + 1

        left_count = self.left.count_levels()
        right_count = self.right.count_levels()

        return max(left_count, right_count) + 1

    def get_coords(self, x, y, sw, sh):
        to_send = [[x, y, self.data]]
        if self.left:
            to_send += self.left.get_coords(x - sw / 2, y + sh, sw / 2, sh)
        if self.right:
            to_send += self.right.get_coords(x + sw / 2, y + sh, sw / 2, sh)
        return to_send

    def get_lines(self, x, y, sw, sh):
        to_send = []
        if self.left:
            left_coords = self.left.get_coords(x - sw / 2, y + sh, sw / 2, sh)
            to_send += [[x, y, left_coords[0][0], left_coords[0][1]]]
            to_send += self.left.get_lines(x - sw / 2, y + sh, sw / 2, sh)
        if self.right:
            right_coords = self.right.get_coords(x + sw / 2, y + sh, sw / 2, sh)
            to_send += [[x, y, right_coords[0][0], right_coords[0][1]]]
            to_send += self.right.get_lines(x + sw / 2, y + sh, sw / 2, sh)
        return to_send

    def show_tree(self):
        self.refresh_parents()
        tree_height = self.count_levels()
        max_tree_width = 2 ** (tree_height - 1)
        window_height = 512 * 1.25
        window_width = 512 * 1.5
        node_radius = window_width / max_tree_width / 2
        node_radius = min(node_radius, 10)
        window = Tk()
        window.title("Binary Tree")  # Set a title
        canvas = Canvas(window, width=window_width + 100, height=window_height + 100, bg="white")
        canvas.pack()
        window_height = int((window_height - 2 * tree_height * node_radius) / tree_height)
        lines_to_draw = self.get_lines(50 + window_width / 2, 50 + node_radius, window_width / 2, window_height)
        for line_to_draw in lines_to_draw:
            x1 = line_to_draw[0]
            y1 = line_to_draw[1]
            x2 = line_to_draw[2]
            y2 = line_to_draw[3]
            canvas.create_line(x1, y1, x2, y2)
        nodes_to_draw = self.get_coords(50 + window_width / 2, 50 + node_radius, window_width / 2, window_height)
        for node_to_draw in nodes_to_draw:
            x = node_to_draw[0]
            y = node_to_draw[1]
            text = node_to_draw[2]
            if node_radius >= 10:
                canvas.create_oval(x - node_radius, y - node_radius, x + node_radius, y + node_radius, fill="white")
            canvas.create_text(x, y, text=text)

        window.mainloop()

    def insert(self, data):
        """
        Insert new node with data

        :param data: node data object to insert
        :raises ValueError: data is already present in the tree
        """
        if self.data is None:
            self.data = data
            return

        if data < self.data:
            if self.left is not None:
                self.left.insert(data)
                return

            self.left = Node(data)
            self.left.parent = self
            return

        if data > self.data:
            if self.right is not None:
                self.right.insert(data)
                return

            self.right = Node(data)
            self.right.parent = self
            return

        raise ValueError("data is already present in the tree")

    def rotate_right(self):
        """
        rotate the tree to the right such that this node becomes the right child of the new root

        :raises ValueError: Can't rotate to the right as there is no 'right' node to rotate from
        """
        if self.left is None:
            raise ValueError("Can't rotate to the right as there is no 'left' node to rotate from")

        new_root = Node(None)

        old_root = Node(None)
        old_root.parent = new_root

        new_root.__replace(data=self.left.data, left=self.left.left, right=old_root)
        old_root.__replace(data=self.data, left=self.left.right, right=self.right)

        self.__replace_with_node(new_root)

    def rotate_left(self):
        """
        rotate the tree to the left such that this node becomes the left child of the new root

        :raises ValueError: Can't rotate to the left as there is no 'right' node to rotate from
        """
        if self.right is None:
            raise ValueError("Can't rotate to the left as there is no 'right' node to rotate from")

        new_root = Node(None)

        old_root = Node(None)
        old_root.parent = new_root

        new_root.__replace(data=self.right.data, left=old_root, right=self.right.right)
        old_root.__replace(data=self.data, left=self.left, right=self.right.left)

        self.__replace_with_node(new_root)

    def get_highest_child(self):
        """
        get the highest of the two child nodes

        :return: child Node with the greatest height
        :raises ValueError: node has no children
        """
        if (self.left is None) and (self.right is None):
            raise ValueError("node has no children")

        if self.left is None:
            return self.right

        if self.right is None:
            return self.left

        left_height, right_height = self.left.get_height(), self.right.get_height()
        if left_height > right_height:
            return self.left
        else:
            return self.right

    #####################################################################################################
    #                                                                                                   #
    #                                EDIT THE CODE BELOW                                                #
    #                                                                                                   #
    #####################################################################################################

    # 1)Implement get_height
    # 2)Implement unbalanced
    # 3)Implement balance's cases
    # 3)Finish rebalance_insert and rebalance_delete
    # 4)Edit insert and delete to call the rebalance functions

    def get_height(self):
        """
        Should run on the node and return the height of the node.
        :return integer:
        """
        ...
        x=self
        y=self
        lheight=1
        rheight=1
        while x.left != None:
            lheight +=1
            x=x.left
        while y.right != None:
            rheight +=1
            y=y.right
        if lheight>rheight:
            return lheight
        return rheight
        
            

    def unbalanced(self):
        """
        Should run on the node and return True if the subtree rooted at the node is unbalance, return False if
        the subtree rooted at this node is balanced.
        :return boolean:
        """
        ...

    @classmethod
    def balance(cls, x, y, z):
        """
        Takes three nodes such that x.parent = y, y.parent = z and balances them

        :param x: Bottommost node
        :param y: Middle node
        :param z: Topmost node
        """
        case = RestructuringCase.determine_case(x, y, z)
        if case == RestructuringCase.Balanced:
            return

        if case == RestructuringCase.LeftLeft:
            ...
            return

        if case == RestructuringCase.LeftRight:
            ...
            return

        if case == RestructuringCase.RightRight:
            ...
            return

        if case == RestructuringCase.RightLeft:
            ...
            return

        raise NotImplementedError("Unexpected restructuring case")

    def rebalance_insert(self):
        x = self
        if not x.parent:
            return
        y = x.parent
        if not y.parent:
            return
        z = y.parent
        while (not z.unbalanced()) and z.parent:
            (x, y, z) = (y, z, z.parent)

        if not z.unbalanced():
            return

        self.balance(x, y, z)
        # and finally
        ...

    def rebalance_delete(self):
        z = self
        while (not z.unbalanced()) and z.parent:
            z = z.parent

        y = z.get_highest_child()
        x = y.get_highest_child()

        if not z.unbalanced():
            return

        self.balance(x, y, z)
        # and finally
        ...
