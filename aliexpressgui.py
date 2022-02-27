import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from scrapy.crawler import CrawlerRunner
from scrapy.exceptions import CloseSpider
from scrapy.spiderloader import SpiderLoader
from scrapy.utils import project
from scrapy.utils.log import configure_logging
from twisted.internet import reactor


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Ali Express Product Scraper')
        self.geometry('400x200')
        self.resizable(0, 0)
        self.use_proxy = tk.StringVar(self)
        self.proxy_path = tk.StringVar(self, value='Proxy file(txt)')
        self.proxy_path_abs = None
        self.keyword_text = tk.StringVar(self,
                                         value='https://www.aliexpress.com/premium/category/200118008.html?CatId=200118008&spm=a2g0o.productlist.0.0.466f7183npYtzL')
        self.ouput = tk.StringVar(self)
        self.folder_path_text = tk.StringVar(
            self, value=os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop'))

        self.execute_thread = None
        self.feed_options = ['json', 'csv']
        self.feed_text = tk.StringVar(self, value=self.feed_options[1])
        self.chosen_spider = tk.StringVar(self)
        self.chosen_spider.set('Select')
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=1)
        self.log_console = None

        self.is_single = tk.IntVar()

        self.__create_widgets()

    def __create_widgets(self):
        input_frame = ttk.Frame(self)
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=3)
        ttk.Label(input_frame, text='Find(Keyword or URL):').grid(column=0, row=0, sticky=tk.W)
        ttk.Checkbutton(input_frame, text='Single Product', variable=self.is_single).grid(column=1, row=1, sticky=tk.W)
        keyword = ttk.Entry(input_frame, width=30, textvariable=self.keyword_text)
        keyword.focus()
        keyword.grid(column=1, row=0, sticky=tk.W)

        lbl_frame = ttk.LabelFrame(input_frame, text='Feed Type:')
        lbl_frame.grid(column=0, row=2, sticky='W')
        ttk.Combobox(lbl_frame, textvariable=self.feed_text, values=self.feed_options, width=10).grid(column=0, row=0,
                                                                                                      sticky=tk.W)
        input_frame.grid(column=0, row=0, sticky='NW')

        for widget in input_frame.winfo_children():
            widget.grid(padx=0, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.columnconfigure(0, weight=1)
        spiders = [s for s in self.get_spiders()]

        ttk.Combobox(button_frame, textvariable=self.chosen_spider, values=spiders, width=10).grid(column=0, row=0,
                                                                                                   sticky=tk.W)
        ttk.Button(button_frame, text='Start', command=lambda: self.execute_threading(None)).grid(column=0, row=1)
        ttk.Button(button_frame, text='Save To', command=self.browse_btn).grid(column=0, row=2)
        ttk.Label(button_frame, text='save_path', textvariable=self.folder_path_text, wraplength=50).grid(column=0,
                                                                                                          row=3)
        button_frame.grid(column=1, row=0, sticky='NW')
        for widget in button_frame.winfo_children():
            widget.grid(padx=0, pady=5)
        for widget in self.winfo_children():
            widget.grid(padx=0, pady=3)

    # def browse_proxy(self):
    #     if self.use_proxy.get():
    #         file_path = filedialog.askopenfilename(filetypes=[("Text File", "*.txt")])
    #         self.proxy_path.set(os.path.basename(file_path))
    #         self.proxy_path_abs = file_path
    #         if not file_path:
    #             self.use_proxy.set(0)

    def browse_btn(self):
        folder_path = filedialog.askdirectory()
        self.folder_path_text.set(folder_path)

    def get_spiders(self):
        return [s for s in SpiderLoader.from_settings(project.get_project_settings()).list()]

    def choose_feed(self, value):
        self.feed_text.set(value)

    def execute_spider(self):

        if self.keyword_text.get() == '':
            messagebox.showerror(
                'Error', 'Keyword should not be None')
            self.execute_thread = None
            return
        if self.chosen_spider.get() == 'Select':
            messagebox.showerror(
                'Error', 'Please choose category or store')
            self.execute_thread = None
            return
        if self.feed_text.get() not in self.feed_options:
            messagebox.showerror(
                'Error', 'Please choose an output Feed')
            self.execute_thread = None
            return
        try:
            output_url = f'file:///{self.folder_path_text.get()}/ali-{self.chosen_spider.get()}-{datetime.now().strftime("%d-%m-%H-%M-%S")}.{self.feed_text.get()}'

            setting = project.get_project_settings()

            setting.set('FEEDS', {output_url: {'format': self.feed_text.get()}})
            configure_logging()
            r = CrawlerRunner(setting)
            d = r.crawl(self.chosen_spider.get(), keyword=self.keyword_text.get(), is_single=self.is_single.get())

            d.addBoth(lambda _: reactor.stop())
            reactor.run(installSignalHandlers=False)
            messagebox.showinfo('success', 'All Value has been Scraped')

        except CloseSpider as err:
            messagebox.showerror('Stopped', err.reason)
            self.execute_btn['state'] = 'enable'

    def item_scraped(self, item):
        if self.log_console:
            self.log_console.insert(tk.END, item)
        return item

    def console_windows(self):
        self.log_win = tk.Toplevel(self)
        self.log_win.protocol("WM_DELETE_WINDOW", self.close_console_windows)
        self.log_console = ScrolledText(self.log_win, width=100, height=20)
        self.log_console.grid(column=1, row=1, rowspan=4)

    def close_console_windows(self):
        self.log_win.destroy()
        self.log_console = None

    def execute_threading(self, event):
        self.execute_thread = threading.Thread(
            target=self.execute_spider, daemon=True)
        if self.execute_thread is not None:
            try:
                if not self.execute_thread.is_alive():
                    self.execute_thread.start()
                    self.after(10, self.check_thread)
            except AttributeError:
                pass

    def check_thread(self):
        if self.execute_thread.is_alive():
            self.after(10, self.check_thread)


if __name__ == '__main__':
    root = App()
    root.attributes('-topmost', True)
    root.mainloop()
