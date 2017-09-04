"""
Performs a number of transformations to convert csv files detailing raw packets
into useful dataset of featurized network flows.
Many insights have been derived from: https://github.com/hmishra2250
Some of the source code for featurization is from hmishra.
"""

import sframe as sf
import csv

headers = ['Source Port', 'Destination Port', 'Score', 'Source', 'Destination', 'Protocol', 'IP_Flags', 'Length', 'Protocols in frame', 'Time', 'tcp_Flags', 'TCP Segment Len', 'udp_Length']


def score_packets(input_url='data/raw_packets.csv', output_url='data/scored_packets.csv'):
  '''
  Take a CSV of packets and score them for botnets
  '''
  print("Transforming initial data csv")
  with open(output_url, 'w') as raw_flows:
    writer = csv.writer(raw_flows, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    with open(input_url) as csvfile:
      writer.writerow(headers + "Score")
      first = True
      for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
        if first is True:
          first = False
          continue
        if row[headers.index('Label')] == "BENIGN":
          row.append(0)
        else:
          row.append(1)
        writer.writerow(row)


def featurize_packets(input_url='data/scored_packets.csv', output_url='data/featurized_packets.csv'):
  pass


def generate_flows(input_url='data/scored_packets.csv', output_url="data/raw_flows.csv"):
  '''
  Generate raw network flows from the packets
  '''
  def __flow_id(x):
    if x['Source'] > x['Destination']:
      return x['Source'] + '-' + x['Destination'] + '-' + str(x['Source Port']) + '-' + str(x['Destination Port']) + '-' + str(x['Protocol'])
    else:
      return x['Destination'] + '-' + x['Source'] + '-' + str(x['Destination Port']) + '-' + str(x['Source Port']) + '-' + str(x['Protocol'])

  sorted_flow = sf.SFrame.read_csv(input_url, verbose=False)
  sorted_flow = sorted_flow[(sorted_flow['Source Port'] != '') & (sorted_flow['Destination Port'] != '')]
  sorted_flow['tcp_Flags'] = sorted_flow['tcp_Flags'].apply(lambda x: int(x, 16) if x != '' else 0)
  sorted_flow['UFid'] = sorted_flow.apply(lambda x: __flow_id(x))
  sorted_flow = sorted_flow.sort(['UFid', 'Time'])

  packet_flow_memberships = []

  current_flow = 0
  current_ufid = None
  start_time = None

  for row in sorted_flow:
    if current_ufid is None:
      if start_time is None:
        start_time = row['Time']
      packet_flow_memberships.append(current_flow)
      current_ufid = row['UFid']
    elif (row['UFid'] == current_ufid):
      # Terminate connection.
      if row['tcp_Flags'] & 1:
        packet_flow_memberships.append(current_flow)
        current_ufid = None
        start_time = None
        current_flow += 1
      # Time-outs
      # elif row['Time'] - startTime >= 360000:
        # current_flow_id = current_flow_id + 1
        # Flow.append(current_flow_id)
        # prev_flow_id = None
        # startTime = row['Time']
      else:
        packet_flow_memberships.append(current_flow)
        current_ufid = row['UFid']
    else:
      current_flow = current_flow + 1
      packet_flow_memberships.append(current_flow)
      current_ufid = row['UFid']
      start_time = row['Time']

  sorted_flow['FlowNo.'] = sf.SArray(packet_flow_memberships)
  sorted_flow.save(output_url)


def featurize_flows(input_url="data/raw_flows.csv", output_url="data/featurized_flows.csv"):
  '''
  Featurize network flows
  '''
  def __is_packet_null(x):
    if (x['TCP Segment Len'] == '0' or x['udp_Length'] == 8):
      return 1
    elif ('ipx' in x['Protocols in frame'].split(':')):
      l = x['Length'] - 30
      if ('eth' in x['Protocols in frame'].split(':')):
        l = l - 14
      if ('ethtype' in x['Protocols in frame'].split(':')):
        l = l - 2
      if ('llc' in x['Protocols in frame'].split(':')):
        l = l - 8
      if (l == 0 or l == -1):
        return 1
    return 0

  flow_list = sf.SFrame.read_csv(input_url, verbose=False)

  # Add time feature, giving initial timestamp of the flow
  # Use initial timestamp to fetch only first packets
  FIRST_PACKETS = flow_list.join(flow_list.groupby(['FlowNo.'], {'Time': sf.aggregate.MIN('Time')}), on=['FlowNo.', 'Time'])[['FlowNo.', 'Length']].unique()
  flow_list = flow_list.join(FIRST_PACKETS.groupby(['FlowNo.'], {'FirstPacketLength': sf.aggregate.AVG('Length')}), on='FlowNo.')
  del(FIRST_PACKETS)

  # Count number of packets per flow
  flow_list = flow_list.join(flow_list.groupby(['FlowNo.'], {'NumberOfPackets': sf.aggregate.COUNT()}), on='FlowNo.')

  # Total number of bytes exchanged
  flow_list = flow_list.join(flow_list.groupby(['FlowNo.'], {'NumberOfBytes': sf.aggregate.SUM('Length')}), on='FlowNo.')

  # Standard deviation of packet length
  flow_list = flow_list.join(flow_list.groupby(['FlowNo.'], {'StdDevOfPacketLength': sf.aggregate.STDV('Length')}), on='FlowNo.')

  # Porportion of packets with same length
  flow_list = flow_list.join(
      flow_list.groupby(['FlowNo.'], {
          'RatioOfSameLengthPackets': sf.aggregate.COUNT_DISTINCT('Length') * 1.0 / sf.aggregate.COUNT()
      }), on='FlowNo.')

  # Calculate duration of flow
  flow_list = flow_list.join(
      flow_list.groupby(['FlowNo.'], {
          'Duration': sf.aggregate.MAX('Time') - sf.aggregate.MIN('Time')
      }), on='FlowNo.')

  # Calculate average packets per second
  flow_list['AveragePacketsPerSecond'] = flow_list.apply(lambda x: x['Duration'] if x['Duration'] == 0.0 else (x['NumberOfPackets'] * 1.0 / x['Duration']))

  # Calculate number of bits per second
  flow_list['AverageBitsPerSecond'] = flow_list.apply(lambda x: 0.0 if x['Duration'] == 0.0 else (x['NumberOfBytes'] * 8.0 / x['Duration']))

  # Calculate average packet length
  flow_list = flow_list.join(flow_list.groupby(['FlowNo.'], {'AveragePacketLength': sf.aggregate.AVG('Length')}), on='FlowNo.')

  # Calculate null packets
  flow_list['IsNull'] = flow_list.apply(lambda x: __is_packet_null(x))

  # Calculate total number of null packets
  flow_list = flow_list.join(flow_list.groupby(['FlowNo.'], {'NumberOfNullPackets': sf.aggregate.SUM('IsNull')}), on='FlowNo.')

  # Added number of forward packets
  flow_list['Forward'] = flow_list.apply(lambda x: 1 if x['Source'] > x['Destination'] else 0)
  flow_list = flow_list.join(flow_list.groupby('FlowNo.', {'NumberOfForwardPackets': sf.aggregate.SUM('Forward')}), on='FlowNo.')

  # Update flows
  flow_list = flow_list.groupby('FlowNo.', {
      'Score': sf.aggregate.SELECT_ONE('Score'),
      'Destination': sf.aggregate.SELECT_ONE('Destination'),
      'Destination Port': sf.aggregate.SELECT_ONE('Destination Port'),
      'Source': sf.aggregate.SELECT_ONE('Source'),
      'Source Port': sf.aggregate.SELECT_ONE('Source Port'),

      'IP_Flags': sf.aggregate.SELECT_ONE('IP_Flags'),
      'Length': sf.aggregate.SELECT_ONE('Length'),
      'Protocol': sf.aggregate.SELECT_ONE('Protocol'),
      'Protocols in frame': sf.aggregate.SELECT_ONE('Protocols in frame'),
      'udp_Length': sf.aggregate.SELECT_ONE('udp_Length'),
      'tcp_Flags': sf.aggregate.SELECT_ONE('tcp_Flags'),
      'Time': sf.aggregate.SELECT_ONE('Time'),
      'TCP Segment Len': sf.aggregate.SELECT_ONE('TCP Segment Len'),

      'FirstPacketLength': sf.aggregate.SELECT_ONE('FirstPacketLength'),
      'NumberOfPackets': sf.aggregate.SELECT_ONE('NumberOfPackets'),
      'NumberOfBytes': sf.aggregate.SELECT_ONE('NumberOfBytes'),
      'StdDevOfPacketLength': sf.aggregate.SELECT_ONE('StdDevOfPacketLength'),
      'RatioOfSameLengthPackets': sf.aggregate.SELECT_ONE('RatioOfSameLengthPackets'),
      'Duration': sf.aggregate.SELECT_ONE('Duration'),
      'AveragePacketLength': sf.aggregate.SELECT_ONE('AveragePacketLength'),
      'AverageBitsPerSecond': sf.aggregate.SELECT_ONE('AverageBitsPerSecond'),
      'AveragePacketsPerSecond': sf.aggregate.SELECT_ONE('AveragePacketsPerSecond'),
      'IsNull': sf.aggregate.SELECT_ONE('IsNull'),
      'NumberOfNullPackets': sf.aggregate.SELECT_ONE('NumberOfNullPackets')
  })
  flow_list.save(output_url)


if __name__ == "__main__":
  score_packets()
  print("Packets scored")
  generate_flows()
  print("Flows generated")
  featurize_flows()
  print("Flows featurized")

