"""
This file will contain a class for extensive form games.
"""

class ExtensiveFormGame():
    """
    """
    def __init__(self, argument , name = False):
        """
        ExtensiveFormGame can take input in the form of a Root::


            sage: player1 = Player('Player 1')
            sage: player2 = Player('Player 2')
            sage: leaf_1 = Leaf({'Player 1': 0, 'Player 2': 1})
            sage: leaf_2 = Leaf({'Player 1': 1, 'Player 2': 0})
            sage: leaf_3 = Leaf({'Player 1': 2, 'Player 2': 4})
            sage: leaf_4 = Leaf({'Player 1': 2, 'Player 2': 1})
            sage: node_1 = Node({'A': leaf_1, 'B': leaf_2})
            sage: node_2 = Node({'A': leaf_3, 'B': leaf_4})
            sage: root_1 = Root({'C': node_1, 'D': node_2})
            sage: egame_1 = ExtensiveFormGame(root_1)
            sage: egame_1.nodes
            Nodes within game are ...
            sage: egame_1.players
            Players within game are ...
            sage: egame_1.gamestructure
            Some long spiel about how the nodes are connected and such? Not sure

        Or it can take a Graph object, so long as it is a tree::

            sage: tree_1 = Graph({root_1:[node_1, node_2], node_1:[leaf_1, leaf_2], node_2:[leaf_3, leaf_4]})
            sage: egame_2 = ExtensiveFormGame(tree_1)
            sage: egame_2.nodes
            Nodes within game are ...
            sage: egame_2.players
            Players within game are ...
            sage: egame_2.gamestructure
            Some long spiel about how the nodes are connected and such? Not sure

        In the above examples, the two games created should be equal

            sage: egame_1 == egame_2
            True


        If we input either a Graph that is not a tree, an error is returned::

            sage: tree_2 = Graph({I'll have to find an example and put it here})
            sage: egame_2 = ExtensiveFormGame(tree_1)
            Traceback (most recent call last):
            ...
            TypeError: Graph inputted is not a tree.


        If we try to put an empty tree in as a game, we'll also return an error::

            sage: tree_3 = Graph()
            sage: egame_2 = ExtensiveFormGame(tree_3)
            Traceback (most recent call last):
            ...
            ValueError: Graph inputted is empty.

        """
    """
    This is only here because I was getting my thoughts out, it probably won't be used much
    if type(argument) is Node:
        argument.is_root == True
        argument.parent == False
        for i in range len(argument.children):  # I need some sort of loop? 

    """
    def set_info_set(nodes):
        """
        We can assign information set to  a set of nodes::

            sage: player1 = Player('Player 1')
            sage: player2 = Player('Player 2')
            sage: leaf_1 = Leaf({'Player 1': 0, 'Player 2': 1})
            sage: leaf_2 = Leaf({'Player 1': 1, 'Player 2': 0})
            sage: leaf_3 = Leaf({'Player 1': 2, 'Player 2': 4})
            sage: leaf_4 = Leaf({'Player 1': 2, 'Player 2': 1})
            sage: node_1 = Node({'A': leaf_1, 'B': leaf_2})
            sage: node_2 = Node({'A': leaf_3, 'B': leaf_4})
            sage: root_1 = Root({'C': node_1, 'D': node_2})
            sage: egame_1 = ExtensiveFormGame(root_1)
            sage: egame_1.set_info_set([node_1, node_2])
            sage: egame_1.set_info_set
            [node_1, node_2]


        If two nodes don't have the same actions, an error is returned::

            sage: player1 = Player('Player 1')
            sage: player2 = Player('Player 2')
            sage: node_1 = Node({'A': leaf_1, 'B': leaf_2})
            sage: node_2 = Node({'DifferentA': leaf_3, 'B': leaf_4})
            sage: leaf_1 = Leaf({'Player 1': 0, 'Player 2': 1})
            sage: leaf_2 = Leaf({'Player 1': 1, 'Player 2': 0})
            sage: leaf_3 = Leaf({'Player 1': 2, 'Player 2': 4})
            sage: leaf_4 = ({'Player 1': 2, 'Player 2': 1})
            sage: root_1 = Root({'C': node_1, 'D': node_2})
            sage: egame_1 = ExtensiveFormGame(root_1)
            sage: egame_1.set_info_set([node_1, node_2])
            Traceback (most recent call last):
            ...
            AttributeError: All nodes in the same information set must have the same actions


        If two nodes have different players, an error is returned::

            sage: player1 = Player('Player 1')
            sage: player2 = Player('Player 2')
            sage: leaf_1 = Leaf({'Player 1': 0, 'Player 2': 1})
            sage: leaf_2 = Leaf({'Player 1': 1, 'Player 2': 0})
            sage: leaf_3 = Leaf({'Player 1': 2, 'Player 2': 4})
            sage: leaf_4 = ({'Player 1': 2, 'Player 2': 1})
            sage: node_1 = Node({'A': leaf_1, 'B': leaf_2})
            sage: node_2 = Node({'A': leaf_3, 'B': leaf_4})
            sage: node_1.player = 'Player 1'
            sage: node_2.player = 'Player 2'
            sage: root_1 = Root({'C': node_1, 'D': node_2})
            sage: egame_1 = ExtensiveFormGame(root_1)
            sage: egame_1.set_info_set([node_1, node_2])
            Traceback (most recent call last):
            ...
            AttributeError: All nodes in the same information set must have the same players.

        """


class Node():
    def __init__(self, argument, name = False, player = False, is_root = False):
        """
        Node input will be in a dictionary format, consisting of the actions and the children of that node::

            sage: player1 = Player('Player 1')
            sage: player2 = Player('Player 2')
            sage: child_1 = Leaf({'Player 1': 0, 'Player 2': 1}, 'Child 1')
            sage: child_2 = Leaf({'Player 1': 1, 'Player 2': 0}, 'Child 2')
            sage: mother_node = Node({'Action1': child_1, 'Action2': child_2}, 'Child 2')
            sage: mother_node.actions
            ['Action1', 'Action2']
            sage: mother_node.children
            ['Child 1', 'Child 2']


        If we then create a second node, who has :code:`mother_node` as one of it's children,
        then the parent of :code:`mother_node` will be set to that node::

            sage: sisternode = Node(['inputhere'])
            sage: mother_node.parent
            False
            sage: grandmother_node = Node({'ActionA':mother_node, 'ActionB':sisternode}, 'Node A')
            sage: mother_node.parent
            An extensive form game node - Node A


        Nodes can also be created without specifying children or parents by just passing the list of actions.
        This so that that nodes can be passed via a Tree Sage graph object to the extensive form game class::

            sage: grandmother_node = Node(['ActionA', 'ActionB'])
            sage: grandmother_node.children
            False
            sage: grandmother_node.parent
            False


        If we try to pass an argument that isn't a dictionary or a list, an error is returned::

            sage: grandmother_node = Node({'ActionA', 'ActionB'})
            Traceback (most recent call last):
            ...
            TypeError: Node must be passed an argument in the form of a dictionary or a list.


        If we try to create a game where a node is its own child/parent, an error is returned::
            sage: false_node = Node([])
            sage: false_node = Node({'Action1': child_1, 'Action2': false_node})
            Traceback (most recent call last):
            ...
            AttributeError: Node cannot have itself as a child or parent.

        If at any point a node is created such that their parent is also their child, an error is returned::

            sage: false_node = Node({'Action1': child_1, 'Action2': child_2})
            sage: child_1 = Node({'A': false_node, 'B': mother_node})
            Traceback (most recent call last):
            ...
            AttributeError: Node parent cannot also be a child of that Node.

        """

        self.player = player
        self.name = name

        self.actions = False

        self.children = False

        self.parent = False

        self.is_root = False

        if type(argument) is dict:
            self.actions = argument.keys()
            self.children = argument.values()
            for child in self.children:
                child.parent = self

            for i in range(len(self.children)): 
                (self.children)[i] = (self.children)[i].name  # Stops the list becoming [Extensive Form Node - Namehere, ...] which could take up a lot of space
                """
                This is the code I was thinking of using, it doesn't work here, nor does it work at all, but it has the vague idea.
                It corresponds to the last two tests on the Node function. I think it might not work because I need to work more with __repr__ on leaf and root?
                if ((self.children)[i]) is self.name:
                    raise AttributeError("Node cannot have itself as a child or parent.")
                if ((self.children)[i]) is self.parent:
                    raise AttributeError("Node parent cannot also be a child of that Node.")  
                # Note: probably could be worded better
                """

        elif type(argument) is list:
            self.actions = argument

        else:
            raise TypeError("Node must be passed an argument in the form of a dictionary or a list.")
            

    def __repr__(self):

        s = 'An extensive form game node'
        if self.name:
            s += ' - ' + str(self.name)
        return s

    def attributes():
        """
        We can use this function to check the attributes of each singular node, the following is what would happen if no attibutes are assigned::

            sage: laura_1 = Node(['inputhere'])
            sage: laura_1.attributes
            The node has the following attributes. Actions: False. Children: False. Parent: False. Player: False.
        """
        return "The Node has the following attribues. Actions: %s. Children: %s. Parent: %s. Player: %s" %(self.actions, self.children, self.parent. self.player)

    def _is_complete(self):
        """
            If we create a node where their children aren't specified and no parent is set, the node is considered incomplete::
            sage: b = Node(['Action1', 'Action2'])
            sage: b._is_complete == True
            False


            However, when we do specify all those attributes, the node is then considered complete::
            sage: player1 = Player('Player 1')
            sage: player2 = Player('Player 2')
            sage: child_1 = Leaf({'Player 1': 0, 'Player 2': 1}, 'Child 1')
            sage: child_2 = Leaf({'Player 1': 1, 'Player 2': 0}, 'Child 2')
            sage: mother_node = Node({'Action1': child_1, 'Action2': child_2}, 'Node B')
            sage: sisternode = Node(['inputhere'])
            sage: grandmother_node = Node({'ActionA':mother_node, 'ActionB':sisternode}, 'Node A')
            sage: mother_node._is_complete()
            True
        """
        return all([self.parent , self.actions, self.children])

    def to_root():
        """
        If a node has no parents, and a Root node hasn't been set, a node can become a Root node::

            sage: andy_1 = Node(['inputhere'])
            sage: type(andy_1) is Node
            True
            sage: type(andy_1) is Root
            False
            sage: andy_1.to_root
            sage: type(andy_1) is Root
            True
            sage: type(andy_1) is Node
            False

        If the node has parents, an error message will be returned::

            sage: andy_1 = Node(['inputhere'])
            sage: andy_2 = Node((['inputhere'])
            sage: dave_1 = Node({'A': andy_1, 'B': andy_2})
            sage: andy_1.to_root
            Traceback (most recent call last):
            ...
            AttributeError: Node with parents cannot be a Root.


        If the node is connected to a set of nodes that have a Root associated with them, an error is returned::

            sage: helen_1 = Root(['inputhere'])
            sage: helen_2 = Root(['inputhere'])
            sage: jill_1 = Node({'A': helen_1, 'B': helen_2})
            sage: jill_1.to_root
            Traceback (most recent call last):
            ...
            AttributeError: Extensive Form Game cannot have two Roots
        """

        
    def to_leaf(payoffs):
        """
        A node can also be changed into a leaf if it has no parents, children, or actions. (i.e it is a blank node)::
            sage: player1 = Player('Player 1')
            sage: player2 = Player('Player 2')
            sage: jones_1 = Node(['inputhere'])
            sage: type(jones_1) is Leaf
            False
            sage: jones_1.to_leaf([{'Player 1': 0, 'Player 2': 1}])
            sage: type(jones_1) is Leaf
            True
            sage: type(jones_1) is Node
            False


        If a node has any attribues other than parent, an error is returned::

            sage: williams_1 = Node(['A', 'B'])
            sage: williams_1.to_leaf([{'Player 1': 0, 'Player 2': 1}])
            Traceback (most recent call last):
            ...
            AttributeError: Node has attributes other than parent, cannot be leaf.

        """


class Leaf():
    def __init__(self, argument, name = False):
        """
        We can check payoffs of any leaf.
            sage: player_1 = Player('player 1')
            sage: player_2 = Player('player 2')
            sage: leaf_1 = Leaf({'player 1': 0, 'player 2': 1})
            sage: leaf_1.payoffs
            {'player 1': 0, 'player 2': 1}
            sage: leaf_1.payoffs[player_1]
            0
            sage: leaf_1.payoffs[player_2]
            1
        """
        self.payoffs = argument
        self.name = name


class Root(Node):
    """
    A Root is just another type of node, so we can get attributes, however :code:`parent` will always be :code:`False`.. Attempting to add a parent will return an error::

        sage: jess_1 = Node(['Green', 'Yellow'])
        sage: jess_2 = Node(['Green', 'Yellow'])
        sage: jess_3 = Node(['Green', 'Yellow'])
        sage: bethan_1 = Root({'Red': jess_1, 'Blue': jess_2})
        sage: bethan_1.attribues
        some output of attributes specific to bethan_1


    We cannot have more than one Root in a game, so if we try to connect a second Root to a connected set of nodes that already have a Root, an error will be displayed::

        sage: jess_1 = Node(['Green', 'Yellow'])
        sage: jess_2 = Node(['Green', 'Yellow'])
        sage: jess_3 = Node(['Green', 'Yellow'])
        sage: bonnie_1 = Root({'Black': jess_1, 'White': jess_3})
        Traceback (most recent call last):
        ...
        AttributeError: Extensive Form Game cannot have two Roots
    """


class Player():
    def __init__(self, name):
        """
        We can use Player() to assign players to nodes::
            sage: jack_1 = Node([0, 1])
            sage: jack_1.player = (Player('Jack'))
            sage: jack_1.player
            Jack


        If a node is not specificed a player, then this should return false::
            sage: sam_1 = Node([0, 1])
            sage: sam_1.player
            False


        We can create players and assign them names::
            sage: ben_player = Player('Benjamin')
            sage: ben_player.name
            'Benjamin'
        """
        self.name = name


    def __repr__(self):

        return self.name