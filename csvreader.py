import csv
from itertools import accumulate


class CSV_worker():
    def __init__(self,filepath):
        try:
            file_ = open(file=filepath,encoding='UTF-8',newline='')
        except:
            raise Exception('file not found')
        self.path = filepath
        self.reader_ = csv.DictReader(file_)
        self.fieldnames_ = self.reader_.fieldnames
        self.data_ = []

    def read(self):
        for i in self.reader_:
            self.data_.append(i)
        return self.data_
    
    def write(self,u):
        self.data_.append(u)

    def delete(self,u):
        self.data_.pop(u)

    def select(self,col,name):
        res = []
        for i in self.data_:
            if (str(i[col]).find(name) != -1):
                res.append(i)
        return res

    def save(self):
        with open(file=self.path,mode='w',encoding='UTF-8',newline='') as file:
            writer = csv.DictWriter(file,fieldnames=self.fieldnames_)
            writer.writeheader()
            writer.writerows(self.data_)




