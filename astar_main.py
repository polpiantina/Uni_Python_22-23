import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import DISABLED
from tkinter import NORMAL
import itertools
import heapq
import time
import random
import networkx as nx
import matplotlib.pyplot as plt
from Levenshtein import distance as lev

class WordPathFinder:
    def __init__(self, dictionary_file):
        self.load_dictionary(dictionary_file)
        self.memo = {}
        self.neighbors = {}

    def load_dictionary(self, dictionary_file):
        self.dictionary = set()
        with open(dictionary_file, 'r') as file:
            for word in file:
                self.dictionary.add(word.strip())

    def find_path(self, start, end):
        self.visited = set()
        start_time = time.time()
        if start not in self.dictionary:
            self.dictionary.add(start)
        if end not in self.dictionary:
            self.dictionary.add(end)
        if start in self.memo and end in self.memo[start]:
            path = self.memo[start][end]
        else:
            path = self.a_star_search(start, end)
            if start in self.memo:
                self.memo[start][end] = path
            else:
                self.memo[start] = {end: path}
        end_time = time.time()
        self.search_time = end_time - start_time
        return path

    def get_neighbors(self, word):
        if word in self.neighbors:
            return self.neighbors[word]
        neighbors = set()
        
        # Generate neighbors by substitutions, insertions, or deletions of letters
        # Generating 26 * len of word options is faster than going through all words of same length
        for i in range(len(word)):
            for letter in 'abcdefghijklmnopqrstuvwxyz':
                candidate = word[:i] + letter + word[i+1:]
                if candidate in self.dictionary and candidate != word:
                    neighbors.add(candidate)

        for i in range(len(word) + 1):
            for letter in 'abcdefghijklmnopqrstuvwxyz':
                candidate = word[:i] + letter + word[i:]
                if candidate in self.dictionary and candidate != word:
                    neighbors.add(candidate)

        for i in range(len(word)):
            candidate = word[:i] + word[i+1:]
            if candidate in self.dictionary and candidate != word:
                neighbors.add(candidate)

        # Generate anagrams
        # Generating all permutations is faster than going through all words of same length
        for perm in itertools.permutations(word):
            candidate = ''.join(perm)
            if candidate in self.dictionary and candidate != word:
                neighbors.add(candidate)

        self.neighbors[word] = neighbors
        return neighbors

    def a_star_search(self, start, end):
        start_time_search = time.time()
        heap = [(self.heuristic(start, end), 0, start, [start])]
        while heap:
            (estimated_cost, path_cost, word, path) = heapq.heappop(heap)
            # Time limit is relevant if the second word is not in the dictionary and it has no neighbors
            if time.time() - start_time_search > 20:
                return 
            if word == end:
                return path
            if word not in self.visited:
                self.visited.add(word)
                for next_word in self.get_neighbors(word):
                    if next_word not in self.visited:
                        new_path = path + [next_word]
                        new_path_cost = path_cost + 1
                        heapq.heappush(heap, (new_path_cost + self.heuristic(next_word, end), new_path_cost, next_word, new_path))
                        if word in self.memo:
                            self.memo[word][next_word] = new_path
                        else:
                            self.memo[word] = {next_word: new_path}

    def heuristic(self, word1, word2):
        return lev(sorted(word1), sorted(word2))

    def clear_data(self):
        self.memo.clear()
        self.visited.clear()
        self.neighbors.clear()
        plt.close('all')

    def get_path_graph(self, path):
        if path is None:
            return None
        path_graph = nx.DiGraph()
        for i in range(len(path) - 1):
            path_graph.add_edge(path[i], path[i+1], color='blue')
        for word in path:
            for neighbor in self.get_neighbors(word):
                if neighbor not in path_graph:
                    path_graph.add_node(neighbor, color='lightgray')
                if (word, neighbor) not in path_graph.edges:
                    path_graph.add_edge(word, neighbor, color='lightgray')
        return path_graph

    def get_min_path_graph(self, path):
        if path is None:
            return None
        path_graph = nx.DiGraph()
        for i in range(len(path) - 1):
            path_graph.add_edge(path[i], path[i+1], color='blue')
        return path_graph

class Application(tk.Tk):
    def __init__(self, dictionary_file):
        super().__init__()
        self.title("Word Path Finder")
        self.resizable(False, False)
        self.style = ttk.Style(self)
        self.word_path_finder = WordPathFinder(dictionary_file)
        self.dictionary_list = list(self.word_path_finder.dictionary)
        self.info_text = ""
        self.data_text = ""
        self.path = None

        self.grid_columnconfigure(0, pad=10)
        self.grid_columnconfigure(1, pad=10)
        self.grid_columnconfigure(2, pad=10)
        self.grid_columnconfigure(3, pad=10)
        self.grid_rowconfigure(0, pad=10)
        self.grid_rowconfigure(1, pad=10)
        self.grid_rowconfigure(2, pad=10)
        self.grid_rowconfigure(3, pad=10)
        self.grid_rowconfigure(4, pad=10)
        self.grid_rowconfigure(5, pad=10)
        self.grid_rowconfigure(6, pad=10)
        self.grid_rowconfigure(7, pad=10)

        self.start_label = tk.Label(self, text="Starting word:")
        self.start_label.grid(row=0, column=0, sticky="ew", padx=10)
        self.start_entry = tk.Entry(self)
        self.start_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=10)
        self.start_check = tk.Button(self, text="Random", command=self.start_random)
        self.start_check.grid(row=0, column=3, sticky="ew", padx=10)

        self.end_label = tk.Label(self, text="Ending word:")
        self.end_label.grid(row=1, column=0, sticky="ew", padx=10)
        self.end_entry = tk.Entry(self)
        self.end_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=10)
        self.end_check = tk.Button(self, text="Random", command=self.end_random)
        self.end_check.grid(row=1, column=3, sticky="ew", padx=10)

        self.find_button = tk.Button(self, text="Find Path", command=self.start_search)
        self.find_button.grid(row=2, column=1)
        self.clear_button = tk.Button(self, text="Clear Input", command=self.clear_input)
        self.clear_button.grid(row=2, column=2)

        self.result_text = tk.Text(self, width=50, height=10, state="disabled")
        self.result_text.grid(row=3, column=0, columnspan=4, pady=10, padx=10)

        self.info_label = tk.Label(self)
        self.info_label.grid(row=4, column=0, columnspan=4)
        self.data_label = tk.Label(self)
        self.data_label.grid(row=5, column=0, columnspan=4)

        self.clear_button = tk.Button(self, text="Clear Data", command=self.clear_data)
        self.clear_button.grid(row=6, column=1, columnspan=2)

        self.show_path_button = tk.Button(self, text="Show Path", command=self.show_path, state="disabled")
        self.show_path_button.grid(row=7, column=1, pady=10)
        self.show_graph_button = tk.Button(self, text="Show Neighbors", command=self.show_graph, state="disabled")
        self.show_graph_button.grid(row=7, column=2, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        plt.close('all')
        self.destroy()

    def start_random(self):
        self.start_entry.delete(0, 'end')
        self.start_entry.insert(0,random.choice(self.dictionary_list))

    def end_random(self):
        self.end_entry.delete(0, 'end')
        self.end_entry.insert(0,random.choice(self.dictionary_list))

    def start_search(self):
        self.find_button["state"] = DISABLED
        self.clear_button["state"] = DISABLED
        self.show_graph_button["state"] = DISABLED
        self.show_path_button["state"] = DISABLED
        self.result_text["state"] = NORMAL
        self.result_text.delete('1.0', tk.END)
        self.result_text["state"] = DISABLED
        self.path = self.word_path_finder.find_path(self.start_entry.get(), self.end_entry.get())
        self.info_text = f"Search time: {round(self.word_path_finder.search_time, 4)} seconds, Visited words: {len(self.word_path_finder.visited)}"
        self.data_text = f"Dictionary size: {len(self.word_path_finder.dictionary)}, Memo size: {len(self.word_path_finder.memo)}, Graph size: {sum(len(neighbors) for neighbors in self.word_path_finder.neighbors.values())}"
        if self.path is None:
            self.result_text["state"] = NORMAL
            self.result_text.insert(tk.END, "No path found\n")
            self.result_text["state"] = DISABLED
        else:
            self.result_text["state"] = NORMAL
            for i, word in enumerate(self.path, start=1):
                self.result_text.insert(tk.END, f"{i}. {word}\n")
            self.result_text["state"] = DISABLED
        self.show_graph_button["state"] = NORMAL
        self.show_path_button["state"] = NORMAL
        self.info_label['text'] = self.info_text
        self.data_label['text'] = self.data_text
        self.find_button["state"] = NORMAL
        self.clear_button["state"] = NORMAL

    def clear_input(self):
        self.start_entry.delete(0, 'end')
        self.end_entry.delete(0, 'end')

    def clear_data(self):
        self.word_path_finder.clear_data()
        #self.clear_input()
        self.data_label['text'] = ""
        self.result_text["state"] = NORMAL
        self.result_text.delete('1.0', 'end')
        self.result_text["state"] = DISABLED
        self.info_label['text'] = ""
        self.show_graph_button["state"] = DISABLED
        self.show_path_button["state"] = DISABLED

    def show_graph(self):
        plt.close('all')
        path_graph = self.word_path_finder.get_path_graph(self.path)
        if path_graph is not None:
            colors = [path_graph.nodes[node].get('color', 'blue') for node in path_graph.nodes]
            nx.draw(path_graph, with_labels=True, node_color=colors)
            plt.show()

    def show_path(self):
        plt.close('all')
        min_path_graph = self.word_path_finder.get_min_path_graph(self.path)
        if min_path_graph is not None:
            colors = [min_path_graph.nodes[node].get('color', 'blue') for node in min_path_graph.nodes]
            nx.draw(min_path_graph, with_labels=True, node_color=colors)
            plt.show()

if __name__ == "__main__":
    app = Application("words.italian.txt")
    app.mainloop()
