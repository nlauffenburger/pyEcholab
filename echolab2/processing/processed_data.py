# coding=utf-8

#     National Oceanic and Atmospheric Administration (NOAA)
#     Alaskan Fisheries Science Center (AFSC)
#     Resource Assessment and Conservation Engineering (RACE)
#     Midwater Assessment and Conservation Engineering (MACE)

#  THIS SOFTWARE AND ITS DOCUMENTATION ARE CONSIDERED TO BE IN THE PUBLIC DOMAIN
#  AND THUS ARE AVAILABLE FOR UNRESTRICTED PUBLIC USE. THEY ARE FURNISHED "AS IS."
#  THE AUTHORS, THE UNITED STATES GOVERNMENT, ITS INSTRUMENTALITIES, OFFICERS,
#  EMPLOYEES, AND AGENTS MAKE NO WARRANTY, EXPRESS OR IMPLIED, AS TO THE USEFULNESS
#  OF THE SOFTWARE AND DOCUMENTATION FOR ANY PURPOSE. THEY ASSUME NO RESPONSIBILITY
#  (1) FOR THE USE OF THE SOFTWARE AND DOCUMENTATION; OR (2) TO PROVIDE TECHNICAL
#  SUPPORT TO USERS.

'''

                      CLASS DESCRIPTION GOES HERE

'''
import numpy as np
from ..sample_data import sample_data
#from sample_data import sample_data


class processed_data(sample_data):
    '''
    The processed_data class contains
    '''

    def __init__(self, channel_id, frequency):

        super(processed_data, self).__init__()

        #  set the frequency and channel_id
        self.channel_id = channel_id
        self.frequency = frequency

        #  sample thickness is the vertical extent of the samples in meters
        #  it is calculated as thickness = sample interval(s) * sound speed(m/s) / 2
        #  you should not append processed data arrays with different sample thicknesses
        self.sample_thickness = 0

        #  sample offset is the number of samples the first row of data are offset away from
        #  the transducer face.
        self.sample_offset = 0


    def shift_pings(self, vert_shift):
        """
        shift_pings shifts sample data vertically by an arbitrary amount,
        interpolating sample data to the new vertical axis.

            vert_shift is a scalar or vector n_pings long that contains the
            constant shift for all pings or a per-ping shift respectively.

        """

        #  determine the vertical extent of the shift
        min_shift = np.min(vert_shift)
        max_shift = np.max(vert_shift)
        vert_ext = max_shift - min_shift

        #  determine our vertical axis - this has to be range or depth
        if hasattr(self, 'range'):
            vert_axis = self.range
        else:
            vert_axis = self.depth

        #  if there is a new vertical extent resize our arrays
        if (vert_ext != 0):
            #  determine the number of new samples as a result of the shift
            new_samps = np.ceil(vert_ext.astype('float32') / self.sample_thickness)
            #  and resize (n_samples will be updated in the _resize method)
            old_samps = self.n_samples
            self._resize_arrays(self.n_pings, self.n_samples + new_samps)

        # create the new vertical axis
        new_axis = (np.arange(self.n_samples) * self.sample_thickness) + np.min(vert_axis) + min_shift

        #  check if this is not a constant shift
        if (vert_ext != 0):
            #  not constant, work thru the 2d attributes and interpolate the sample data
            for attr_name in self._data_attributes:
                attr = getattr(self, attr_name)
                if (isinstance(attr, np.ndarray) and (attr.ndim == 2)):
                    for ping in range(self.n_pings):
                        attr[ping,:] = np.interp(new_axis, vert_axis + vert_shift[ping],
                                attr[ping,:old_samps], left=np.nan, right=np.nan)

        # and assign the new axis
        vert_axis = new_axis


    def _resize_arrays(self, new_ping_dim, new_sample_dim):
        """
        _resize_arrays reimplements sample_data._resize_arrays adding updating of the
        n_pings attribute. In the processed data object we assume that all pings contain
        data (unlike, for example EK60.raw_data where data arrays can be larger than
        the actual data loaded.)
        """

        #  call the parent method to resize the arrays (n_samples is updated here)
        super(processed_data, self)._resize_arrays(new_ping_dim, new_sample_dim)

        #  and then update n_pings
        self.n_pings = self.ping_time.shape[0]


    def __str__(self):
        '''
        reimplemented string method that provides some basic info about the RawData object
        '''

        #  print the class and address
        msg = str(self.__class__) + " at " + str(hex(id(self))) + "\n"

        #  print some more info about the ProcessedData instance
        n_pings = len(self.ping_time)
        if (n_pings > 0):
            msg = msg + "                channel(s): ["
            for channel in self.channel_id:
                msg = msg + channel + ", "
            msg = msg[0:-2] + "]\n"
            msg = msg + "                 frequency: " + str(self.frequency)+ "\n"
            msg = msg + "           data start time: " + str(self.ping_time[0])+ "\n"
            msg = msg + "             data end time: " + str(self.ping_time[n_pings-1])+ "\n"
            msg = msg + "           number of pings: " + str(n_pings)+ "\n"
            if (hasattr(self, 'power')):
                n_pings,n_samples = self.power.shape
                msg = msg + ("    power array dimensions: (" + str(n_pings)+ "," +
                        str(n_samples) +")\n")
            if (hasattr(self, 'angles_alongship')):
                n_pings,n_samples = self.angles_alongship.shape
                msg = msg + ("    angle array dimensions: (" + str(n_pings)+ "," +
                        str(n_samples) +")\n")
        else:
            msg = msg + ("  ProcessedData object contains no data\n")

        return msg
