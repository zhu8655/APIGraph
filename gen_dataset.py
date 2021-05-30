import csv
import pickle

csv.field_size_limit(500 * 1024 * 1024)

dismatch = {}
mapping = {}
num = -1
cnt = 1
row_cnt = 0

calls = open('calls_base.txt', 'w', newline='')
calls_writer = csv.writer(calls)

with open('calls_origin.txt') as f_data:
    data = csv.reader(f_data, delimiter=' ')

    for row in data:
        call = []
        for i in range(0, len(row)):
            if row[i] not in dismatch:
                mapping[num] = cnt
                cnt += 1
                dismatch[row[i]] = num
                num -= 1
            call.append(mapping[dismatch[row[i]]])

        calls_writer.writerow(call)
        row_cnt += 1

# with open('method_cluster_mapping_2000.pkl', 'rb') as f_pkl:
#     pkl = pickle.load(f_pkl)

# calls = open('calls_apigraph.txt', 'w', newline='')
# calls_writer = csv.writer(calls)

# with open('calls_origin.txt') as f_data:
#     data = csv.reader(f_data, delimiter=' ')

#     for row in data:
#         call = []
#         for i in range(0, len(row)):
#             if row[i] in pkl:
#                 if pkl[row[i]] not in mapping:
#                     mapping[pkl[row[i]]] = cnt
#                     cnt += 1
#                 call.append(mapping[pkl[row[i]]])
#             else:
#                 if row[i] not in dismatch:
#                     mapping[num] = cnt
#                     cnt += 1
#                     dismatch[row[i]] = num
#                     num -= 1
#                 call.append(mapping[dismatch[row[i]]])

#         calls_writer.writerow(call)
#         row_cnt += 1

print(row_cnt)
print(dismatch)