
# -*- coding: utf-8 -*-
"""The 'DCI' object host file.
This is file information, not the class information. This information is only for the API developers.
Please read the 'DCI' object documentation for details.
Example::
    from packman.apps import DCI
    help( DCI )
Notes:
    * Tutorial: 
    * For more details about the parameters for compliance, or to site this, read the following paper: 
Todo:
    * Finish writing up the documentation.
    * Finish optimizing the performance.
Authors:
    * Ambuj Kumar  (ambuj@iastate.edu)
    * Pranav Khade (https://github.com/Pranavkhade)
"""
import numpy
import more_itertools as mit
from sklearn.metrics import calinski_harabasz_score as chs
from scipy.cluster.hierarchy import ward, fcluster

from ..anm import ANM
from ..molecule import load_structure, download_structure, Protein

class DCI():
    """This class contains the code for DCI analysis.

    Notes:
        * Tutorial:
        * Webserver: 
        * Publication:
    
    Args:
        mol (packman.molecule.Protein) : Structure in the 'Protein' object.
        cutoff (float)                 : GNM distance cutoff. Default set to 7.5
        chain (string)                 : Protein chain id. Default is set to using all chains.
        n_com (int)                    : Number of communities to generate. Default the program will explore best possible cluster numbers for the given data.
    """
        
    def __init__(self, mol, cutoff = 7.0, chain = None, n_com = None):
        self.molObj = mol
        assert type( self.molObj ) == Protein, "mol should be a packman.molecule.Protein object."

        if chain:
            self.atoms = [i for i in self.molObj[0][chain].get_calpha()]
            collect_resi = [i.get_atoms() for i in self.molObj[0][chain].get_residues() if i.get_calpha() != None]
        else:
            self.atoms = [i for i in self.molObj[0].get_calpha()]
            collect_resi = [i.get_atoms() for i in self.molObj[0].get_residues() if i.get_calpha() != None]
            
        if n_com:
            if (n_com < 2) or (n_com > len(self.atoms)):
                raise ValueError("Value of n_com should be 2 or greater but less than or equal to the maximum number of residues in the protein")
                
        if cutoff <= 0:
            raise ValueError("Value of cutoff can only be a positive integer")

        self.cutoff = cutoff
        self.coords = numpy.array([x.get_location() for x in self.atoms])
        self.pdbid = mol.get_id()

        
        self.GNM()
        self.calculate_decomposition()
        self.calculate_crosscorrelation()
        dist_mat = 1-self.C
        
        if n_com:
            self.get_n_communities(dist_mat, n_com)
        else:
            self.calculate_cluster(dist_mat)
        
        self.calcualte_pymol_commands()
        
    #Get functions
    def get_labels(self, community_obj):
        """

        """
        res_store = dict()
        for label, atm in zip(community_obj, self.atoms):

            try:
                res_store[label]
            except:
                res_store[label] = list()
            
            res_store[label].append(str(atm.get_parent().get_id())+atm.get_parent().get_parent().get_id())
            
        return res_store
        
    def get_range(self, iterable):
        """

        """
        for group in mit.consecutive_groups(iterable):
            group = list(group)
            if len(group) == 1:
                yield group[0]
            else:
                yield group[0], group[-1]
    
    def get_n_communities(self, dist_mat, n):
        """
        """
        Data = numpy.triu(dist_mat)
        Z = ward(Data)
        label = fcluster(Z, n, criterion='maxclust')
        return label
        
    def get_movies(self):
        """
        """
        model = ANM(coords = self.coords, atoms = self.atoms)
        model.calculate_hessian()
        model.calculate_decomposition()
        model.calculate_movie(mode_number=6, scale=20.0, n=20)
        model.calculate_movie(mode_number=7, scale=20.0, n=20)
        model.calculate_movie(mode_number=8, scale=20.0, n=20)
        model.calculate_movie(mode_number=9, scale=20.0, n=20)
        model.calculate_movie(mode_number=10, scale=20.0, n=20)
        return True
    
    def get_cluster_labels(self):
        """
        """
        return self.best_community
    
    def get_cc(self):
        """
        """
        return self.C
    
    def get_communities(self):
        """
        """
        return self.store_communities
    
                
    # Model
    def GNM(self):
        gamma = 1.0
        n_atoms=len(self.coords)
        self.GNM_MAT=numpy.zeros((n_atoms, n_atoms), float)
        for i in range(len(self.coords)):
            diff = self.coords[i+1:, :] - self.coords[i]
            squared_diff = diff**2
            for j, s_ij in enumerate(squared_diff.sum(1)):
                if s_ij <= self.cutoff**2:
                    diff_coords = diff[j]
                    j = j + i + 1
                    self.GNM_MAT[i, j] = -gamma
                    self.GNM_MAT[j, i] = -gamma
                    self.GNM_MAT[i, i] = self.GNM_MAT[i, i] + gamma
                    self.GNM_MAT[j, j] = self.GNM_MAT[j, j] + gamma
        
        return True
    
    #Calculate functions
    def calculate_decomposition(self):
        """
        """
        self.eigen_values, self.eigen_vectors = numpy.linalg.eigh(self.GNM_MAT)
        return True
    
    def calculate_crosscorrelation(self):
        """
        """
        n = len(self.atoms)
        EVec=self.eigen_vectors.T
        self.hessian_inv= numpy.matmul( numpy.matmul( EVec[1:].transpose() , numpy.diag(1/self.eigen_values[1:]) ) , EVec[1:] )
        self.C = numpy.zeros((n , n))
        for i in range(n):
            for j in range(n):
                self.C[i, j] = float(self.hessian_inv[i, j])/numpy.sqrt(self.hessian_inv[i, i]*self.hessian_inv[j, j])
                
        return True

    def calculate_windows(self, iterable):
        """Yield range of consecutive numbers.
        """
        store_chain = dict()
        for i in sorted(iterable):
            try:
                store_chain[i[-1]]
            except:
                store_chain[i[-1]] = list()
                
            store_chain[i[-1]].append(int(i[:-1]))
            
        for chain_key, in_iterable in store_chain.items():
            store_chain[chain_key] = list(self.get_range(sorted(list(set(in_iterable)))))
            
        return store_chain
    
    def calculate_cluster(self, dist_mat):
        """
        """
        best_score = 0
        dist_mat = numpy.sqrt(2*(dist_mat))
        Data = numpy.triu(dist_mat)
        Z = ward(Data)
        self.store_communities = dict()
        self.store_score = dict()
        for i in range(2, 21):
            label = fcluster(Z, i, criterion='maxclust')
            self.store_communities[i] = label
            score = chs(dist_mat, label)
            self.store_score[i] = score
            if score > best_score:
                self.best_community = label
                best_score = score
        
        self.store_score = dict(sorted(self.store_score.items(), key=lambda item: item[1])[::-1])
        self.calculate_CH_plot()
        return True
        
        
    def calculate_CH_plot(self):
        """
        """
        import matplotlib.pyplot as plt

        lists = sorted(self.store_score.items()) # sorted by key, return a list of tuples
        x, y = zip(*lists) # unpack a list of pairs into two tuples
        plt.xlabel('Community count', fontsize=14)
        plt.ylabel('CH Score', fontsize=12)
        plt.plot([int(i) for i in x], y)
        plt.xticks(x)
        plt.savefig(self.pdbid+'_CH_Score.png')
        return True
    
    def calcualte_pymol_commands(self,filename='DCI_pymol_output.txt'):
        """
        """
        with open(filename, "w") as fp:
            for key, dynamic_community in self.store_communities.items():
                fp.write("#############################################################\n\n")
                fp.write("Clustering iteration id - C%s\n" %(key-1))
                fp.write("number of communities - %s\n" %(len(list(set(dynamic_community)))))
                fp.write("CH Score - %s\n" %self.store_score[key])
                clust = self.get_labels(dynamic_community)
            
                for key, val in clust.items():
                    clust[key] = self.calculate_windows(val)
                    
                for key, val in clust.items():
                    fp.write("----------------------------------------------------------\n\n")
                    fp.write("cluster %s\n\n" %key)
                    for inkey, inval in val.items():
                        statement = "select resi "
                        for dat in inval:
                            if isinstance(dat, int):
                                statement = statement + "+" + str(dat)
                            else:
                                resi = list(range(dat[0], dat[1]+1))
                                for res in resi:
                                    statement = statement + "+" + str(res)
                            
                        fp.write("%s and chain %s\n" %(statement, inkey))
                    fp.write("----------------------------------------------------------\n\n")
    

def dci_cli(args,mol):
    chain  = args.chain
    cutoff = args.cutoff
    n_com  = args.n_com

    model = DCI( mol, cutoff = cutoff, chain = chain, n_com = n_com )
    return True