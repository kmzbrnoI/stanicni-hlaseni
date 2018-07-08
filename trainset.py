import message_parser


class TrainSet:
    def __init__(self, message):
        self.station = ''
        self.load_train_set(message)

    def load_train_set(self, message):
        parsed = message_parser.parse(message, [';'])

        self.train_number = parsed[0]
        self.train_type = parsed[1]
        self.railway = parsed[2]
        self.start_station = parsed[3]
        self.final_station = parsed[4]

        self.arrival_time = parsed[5] if len(parsed) > 5 else ''
        self.departure_time = parsed[6] if len(parsed) > 6 else ''

    def __str__(self):
        return ("Train number: {0}\n".format(self.train_number) +
                "Train type: {0}\n".format(self.train_type) +
                "Railway: {0}\n".format(self.railway) +
                "Start station: {0}\n".format(self.start_station) +
                "Final station: {0}\n".format(self.final_station) +
                "Arrival time: {0}\n".format(self.arrival_time) +
                "Departure time: {0}\n".format(self.departure_time) +
                "Station: {0}".format(self.departure_time))

    __repr__ = __str__
