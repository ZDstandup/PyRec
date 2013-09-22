from collections import defaultdict
import sys
import codecs
from random import shuffle
from operator import itemgetter

class DataModel:
    

    def load_from_file(self, filename, sep ='\t', format={'value':2, 'row':0, 'col':1}):
            rows = []
            columns = []
            values = []
            sys.stdout.write('Loading %s\n' % filename)

            i = 0
            for line in codecs.open(filename, 'r', 'utf8'):
                data = line.strip('\r\n').split(sep)
                value = None
                if not data:
                    raise TypeError('Data is empty or None!')
                if not format:
                    try:
                        value, row_id, col_id = data
                    except:
                        value = 1
                        row_id, col_id = data
                else:
                    try:
                         # Default value is 1
                        try:
                            value = data[format['value']]
                        except KeyError, ValueError:
                            value = 1
                        try: 
                            row_id = data[format['row']]
                        except KeyError:
                            row_id = data[1]
                        try:
                            col_id = data[format['col']]
                        except KeyError:
                            col_id = data[2]
                        row_id = row_id.strip()
                        col_id = col_id.strip()
                        if format.has_key('ids') and (format['ids'] == int or format['ids'] == 'int'):
                            try:
                                row_id = int(row_id)
                            except:
                                print 'Error (ID is not int) while reading: %s' % data #Just ignore that line
                                continue
                            try:
                                col_id = int(col_id)
                            except:
                                print 'Error (ID is not int) while reading: %s' % data #Just ignore that line
                                continue
                    except IndexError:
                        #raise IndexError('while reading %s' % data)
                        print 'Error while reading: %s' % data #Just ignore that line
                        continue
                # Try to convert ids to int
                try:
                    row_id = int(row_id)
                except: pass
                try:
                    col_id = int(col_id)
                except: pass
                try:
                    value = float(value)
                except: pass
                # Add to list
                try:
                    rows.append(row_id-1)
                    columns.append(col_id-1)
                    values.append(value)
                except:
                    sys.stdout.write('\nError while reading (%s, %s, %s). Skipping this tuple\n' % (value, row_id, col_id))
                i += 1

            self._rows = rows
            self._columns = columns
            self._values = values
            self._data = (rows, columns, values)
            self._size = len(values)

    def get_mean(self):
        if self._mean is not None:
            return self._mean
        else:
            print "The data has not been mean-normalized"
    
    def get_biases(self):
        if self._biases is not None:
            return self._biases
        else:
            print "The data still has user and item biases"
     
    def get_rows(self):
        if self._rows is not None:
            return self._rows
        else:
            print "No elements have been added to the dataset"
    
    def get_columns(self):
        if self._columns is not None:
            return self._columns
        else:
            print "No elements have been added to the dataset"

    def get_values(self):
        if self._values is not None:
            return self._values
        else:
            print "No elements have been added to the dataset"

    def get_training_data(self):
        if self._train is not None:
            return self._train
        else:
            print "There is currently no training data"

    def get_test_data(self):
        if self._test is not None:
            return self._test
        else:
            print "There is currently no test data"

    def get_validation_data(self):
        if self._validate is not None:
            return self._validate
        else:
            print "There is currently no validation data"

    def get_size(self):
        if self._matrix_size is not None:
            return self._matrix_size
        else:
            print "There is no data available"

    def split_train_test(self, training_percentage=.80, normalize=True, remove_bias=True, randomize=False):
        print "Splitting....\n"
        if self._data is None:
            "There is no data to split"
            return

        if randomize:
            randomized_data = self.randomize_data()
            self._rows = randomized_data[0]
            self._columns = randomized_data[1]
            self._values = randomized_data[2]

        num_rows = max(self._rows) + 1
        num_cols = max(self._columns) + 1
        self._matrix_size = (num_rows, num_cols)
        train = int(training_percentage*self._size)
        training_values = self._values[:train]
        if normalize:
            training_values = self._mean_normalize(training_values)
        if remove_bias:
            biased_data = zip(self._rows[:train], self._columns[:train], training_values)
            training_values = self._calculate_bias(bias_data, tuple(self._matrix_size))
        
        self._train = (self._rows[:train], self._columns[:train], training_values)
        self._test = (self._rows[train:], self._columns[train:], self._values[train:])

    def split_train_validate_test(self, training_percentage=.80, normalize=True, remove_bias=True, randomize=False):
        print "Splitting....\n"
        if self._data is None:
            print "There is no data in the data model"
            return

        if randomize:
            randomized_data = self.randomize_data()
            self._rows = randomized_data[0]
            self._columns = randomized_data[1]
            self._values = randomized_data[2]

        train = int(training_percentage*self._size)
        num_rows = max(self._rows) + 1
        num_cols = max(self._columns) + 1
        self._matrix_size = (num_rows, num_cols)
        validate = train + int((self._size - train)/2.0)
        if randomize:
            self._data = self.randomize_data(self._data)
        training_values = self._values[:train]
        if normalize:
            training_values = self._mean_normalize(training_values)
        if remove_bias:
            biased_data = zip(self._rows[:train], self._columns[:train], training_values)
            training_values = self._calculate_bias(biased_data, num_rows, num_cols)

        self._train = (self._rows[:train], self._columns[:train], training_values)
        self._validate = (self._rows[train:validate], self._columns[train:validate], self._values[train:validate])
        self._test = (self._rows[validate:], self._columns[validate:], self._values[validate:])
    
    def _randomize_data(self):
        list1_shuf = []
        list2_shuf = []
        list3_shuf = []
        index_shuf = range(len(self._values))
        shuffle(index_shuf)
        for i in index_shuf:
            list1_shuf.append(self._rows[i])
            list2_shuf.append(self._columns[i])
            list3_shuf.append(self._values[i])
        return(list1_shuf, list2_shuf, list3_shuf)
    
    def _mean_normalize(self, data):
        if data is None:
            print "There is no data to normalize"
            return

        self._mean = float(sum(data))/float(len(data))
        normalized_data = [x - self._mean for x in data]
        return normalized_data
 
    def _calculate_bias(self, data, num_rows, num_cols):
        if data is None:
            print "There is no data to normalize"
            return
        
        print num_rows
        print num_cols
        user_bias = [0] * num_rows
        num_users = defaultdict(int)
        item_bias = [0] * num_cols
        num_items = defaultdict(int)

        for r, c, v in data:
            user_bias[r] += v
            num_users[r] += 1
            item_bias[c] += v
            num_items[c] += 1

        user_bias = [ x/num_users[r]  if num_users[r] != 0 else 0 for r, x in enumerate(user_bias) ]
        item_bias = [ x/num_items[c] if num_items[c] != 0 else 0 for c, x in enumerate(item_bias) ]
        self._biases = (user_bias, item_bias)
        unbiased_data = [v - user_bias[r] - item_bias[c] for r, c, v in data]
        return unbiased_data

