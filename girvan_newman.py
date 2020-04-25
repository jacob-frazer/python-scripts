# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 11:06:04 2020

@author: Jake Frazer
"""

import pandas as pd

# define the nodes and links in a dataframe
graph_data = {
        "vert1":[1,1,2,2,4,4,4,5,6],
        "vert2":[2,3,3,4,5,6,7,6,7]
        }

vertices = set(graph_data["vert1"]+graph_data["vert2"])
edgesDF = pd.DataFrame(graph_data)


def buildTree(node, edgesDF):
    ''' func to take node and build out the full tree for the node - children parents etc
    '''
    stack = [node]    
    tree_data = {}
    visitedNodes = []
    
    # populate the tree data obj - can this be done with a default dict
    for n in vertices:
        tree_data[n] = {"parents":set(), "children":set()}
    
    for node in vertices:
        while stack:
            node = stack.pop(0)
            visitedNodes.append(node)
            
            # get children of node
            children = pd.concat( [ edgesDF.loc[edgesDF['vert1'] == node]["vert2"], edgesDF.loc[edgesDF['vert2'] == node]["vert1"] ] )
        
            # filter any rels to already visited nodes add new children to the stack add tree_data
            for value in children.values:
                
                if value not in visitedNodes:
                    stack.append(value)
                    # putting this here stops same level being considered children
                    tree_data[node]["children"].add( value )
                    tree_data[value]["parents"].add( node )
                    
                    # check if share parent - update to remove from other
                    if tree_data[value]["parents"].intersection(tree_data[node]["parents"]):
                        tree_data[node]["children"].remove(value)                    
                        tree_data[value]["parents"].remove(node)
                    
    return tree_data


class tree():
    
    def __init__(self, graphNodes):
        ''' takes an iterable of graphNode objects and connects all into tree object
        '''
        
        self.graphNodes = {gn.get_name() : gn for gn in graphNodes}
        
        # build out whole object here
        lst = []
        for node in self.graphNodes.values():
            lst += node.list_repr()
            
            # update the node to have knowledeg of the other objs
            node.update_to_objs(self.graphNodes)
            
        self.graphDF = pd.DataFrame(lst, columns=['node ID', 'Children', 'Parents', 'shortest paths', 'credits'])
        
        self.rootNode = self.graphNodes[ self.graphDF[self.graphDF.isnull()['Parents']]['node ID'].values[0] ]
        self.bfs_ordering = self.traverse_from_root(case='bfs')
        return
    
    def search(self, attr, search_val):
        ''' function to search tree object by node ID, children or parents and return
        whatever is found
        ''' 
        found = None
        return found
    
    
    def shortest_paths(self):
        ''' update the vals for shortest paths to that node
        '''
        for node in self.bfs_ordering:
            # if root node
            # updates the node to map to the objects rather than IDs
            sp = node.update_shortest_paths()

            # select rows with correct node id and update the shortest path values
            for index in self.graphDF.loc[self.graphDF['node ID'] == node.get_name()].index:
                self.graphDF.at[index, 'shortest paths'] = sp
            
        return self.graphDF
    
    
    def traverse_from_root(self, case):
        ''' return either path of depth first or breadth first search as list of graph nodes
        '''
        ordering = []
        
        if case == 'bfs':
            # bfs
            # get root then children add etc
            stack = [self.rootNode]
            while stack:
                current_node = stack.pop(0)
                for c in current_node.get_children().values():
                    stack.append(c)
                ordering.append(current_node)
            
            return ordering
        
        return 'Func called without appropriate case'
            
        
    
    def calc_credits(self):
        '''  reversed bfs - to start from leaves - calculates credits
        '''
        for node in reversed(self.bfs_ordering):
            # skip the rels from a leaf 
            if node.leaf:
                continue
            
            for cnid, child in node.get_children().items():
                # add the credits from the rel with this child to the nodes credits
                node.credits += child.parent_credit(node.get_name()) * child.credits
                # update the rel to have the credits of the child credits
                # gets the right index
                index = self.graphDF.loc[(self.graphDF['node ID'] == node.get_name()) & (self.graphDF['Children'] == cnid)].index
                # update index
                self.graphDF.at[index, 'credits'] = child.parent_credit(node.get_name()) * child.credits

        return
        
    def final_rel_credits(self):
        ''' calculates the final new data structure that has the relation and how many credits it got from that tree approach
        
        drop all leaf nodes from graphDF - make all rels go from lower ID to higher ID regardless 4->2 becomes 2->4
        '''
        #final_credits = self.graphDF[self.graphDF["Children"].notnull()]
        rel_cred = []
        for index, row in self.graphDF[self.graphDF["Children"].notnull()].iterrows():
            n1 = row["node ID"]
            n2 = row["Children"]
            credit = row["credits"]
            
            if n1 < n2:
                rel_cred.append([n1, n2, credit])
            else:
                rel_cred.append([n2, n1, credit])
                
        return pd.DataFrame(rel_cred, columns=["node1","node2","credits"])
        
class GraphNode():
    
    def __init__(self, name, children=None, parents=None):
        self.name = name
        self.children = children
        self.parents = parents
        self.root = False if self.parents else True
        self.leaf = False if self.children else True
        self.shortest_paths = 1
        self.credits = 1        # used to help calc edge credits not useful directly - the credits that node gives to ea. parent
        self.objs = False
        return
    
    def get_name(self):
        return self.name
    
    def get_children(self):
        return self.children
    
    def get_parents(self):
        return self.parents
    
    def list_repr(self):
        if not self.get_children():
            self.children = [None]
        if not self.get_parents():
            self.parents = [None]
           
        list_rpr = []
        for c in self.get_children():
            for p in self.get_parents():
                list_rpr.append([self.get_name(), c, p, self.shortest_paths, self.credits])
        return list_rpr
    
    
    def update_to_objs(self, graphNodes):
        ''' change the sets that contain the id of the parents and children to 
        the relative objects they should map to
        '''
        temp_parents = {}
        temp_children = {}
                
        # skip for leaf nodes
        if not self.leaf:
            for child in self.get_children():
                temp_children[child] = graphNodes[child]
            
        # skip for root node
        if not self.root:
            for parent in self.get_parents():
                temp_parents[parent] = graphNodes[parent]
         
        self.children = temp_children
        self.parents = temp_parents
        
        self.objs = True
        self.parent_credits = self.calc_parent_credits()  # calculates how much we need to give for each parent rel

        return True
    
    def update_shortest_paths(self):
        if not self.objs:
            print("Can't run without having ran update_to_objs first")
            return
        
        self.shortest_paths = max(sum([x.shortest_paths for x in self.get_parents().values()]) , 1 )     # stop root from getting 0
        return self.shortest_paths 
    
    
    def calc_parent_credits(self):
        parent_sps = { pid: parent.shortest_paths for pid, parent in self.get_parents().items() }
        total_paths = sum(parent_sps.values())
        return {pid: (self.credits * parent.shortest_paths/total_paths) for pid, parent in self.get_parents().items()}
            
    
    def parent_credit(self, parent_id):
        return self.parent_credits[parent_id]
        
        
## Actual script down here
        
    
outputs = []
# running process with each vertice being the root once
for n in vertices:
    # build tree with n as root vertice
    current_tree = tree([GraphNode(nid, child_parent_dict["children"], child_parent_dict["parents"]) for nid, child_parent_dict in buildTree(n, edgesDF).items()])
    
    # calculate the shortest paths and credits
    current_tree.shortest_paths()
    current_tree.calc_credits()
    
    # return the final standardised obj
    outputs.append(current_tree.final_rel_credits())
    
# concatenate all into one df and reduce df where node1 and node2 are same as another row and sum the credits value
final_df = (((pd.concat(outputs)).groupby(["node1","node2"]).sum())/2).rename(columns={"credits":"betweeness"})

print(final_df)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    