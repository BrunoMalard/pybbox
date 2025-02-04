from .bboxConstant import BboxConstant
from .bboxAuth import BboxAuth
from .bboxApiURL import BboxAPIUrl
from .bboxApiCall import BboxApiCall


class Bbox:
    """
    Class to interact with Bouygues Bbox Modem Routeur
    API Reference used for this : https://api.bbox.fr/doc/apirouter/
    """

    def __init__(self, ip=BboxConstant.DEFAULT_LOCAL_IP):
        """
        Initiate a Bbox instance with a default local ip (192.168.1.254)
        :param ip: Ip of the box if you do not want the default one
        :type ip: str
        :return: A Bbox Api Instance
        :rtype: None
        """
        self.bbox_url = BboxAPIUrl(None, None, ip)
        self.bbox_auth = BboxAuth(None, None, False, self.bbox_url.authentication_type)

    @property
    def get_access_type(self):
        """
        Return if the access is made on the local network or remotely
        :return: AUTHENTICATION_TYPE_LOCAL (0) or AUTHENTICATION_TYPE_REMOTE (1)
        :rtype: int
        """
        return self.bbox_url.authentication_type

    """
    USEFUL FUNCTIONS
    """

    """
    DEVICE API
    """

    def get_bbox_info(self):
        """
        This API returns Bbox information
        :return: numbers of info about the box itself (see API doc)
        :rtype: dict
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PUBLIC, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        self.bbox_url.set_api_name(BboxConstant.API_DEVICE, None)
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_GET, None,
                          self.bbox_auth)
        resp = api.execute_api_request()
        return resp.json()[0]

    def set_display_luminosity(self, luminosity):
        """
        Change the intensity of light of the front panel of the box
        :param luminosity: must be between 0 (light off) and 100
        :type luminosity: int
        """
        if (luminosity < 0) or (luminosity > 100):
            raise ValueError("Luminosity must be between 0 and 100")
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PRIVATE,
                                  BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        self.bbox_url.set_api_name(BboxConstant.API_DEVICE, "display")
        data = {'luminosity': luminosity}
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_PUT, data,
                          self.bbox_auth)
        api.execute_api_request()

    def reboot(self):
        """
        Reboot the device
        Useful when trying to get xDSL sync
        """
        token = self.get_token()
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PRIVATE, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        url_suffix = "reboot?btoken={}".format(token)
        self.bbox_url.set_api_name(BboxConstant.API_DEVICE, url_suffix)
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_POST, None,
                          self.bbox_auth)
        api.execute_api_request()

    def get_token(self):
        """
        Return a string which is a token, needed for some API calls
        :return: Token (can be used with some API call
        :rtype: str

        .. todo:: make a token class to be able to store date of expiration
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PRIVATE, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        self.bbox_url.set_api_name(BboxConstant.API_DEVICE, "token")
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_GET, None,
                          self.bbox_auth)
        resp = api.execute_api_request()
        return resp.json()[0]['device']['token']

    def get_logs(self):
        """
        Return the status logs of the box
        :rtype: list
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PRIVATE, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        self.bbox_url.set_api_name(BboxConstant.API_DEVICE, "log")
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_GET, None,
                          self.bbox_auth)
        resp = api.execute_api_request()
        return resp.json()[0]['log']

    """
    LAN API
    """

    def get_all_connected_devices(self):
        """
        Get all info about devices connected to the box
        :return: a list with each device info
        :rtype: list
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PUBLIC, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        self.bbox_url.set_api_name(BboxConstant.API_HOSTS, None)
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_GET, None,
                          self.bbox_auth)
        resp = api.execute_api_request()
        return resp.json()[0]["hosts"]["list"]

    def is_device_connected(self, ip):
        """
        Check if a device identified by it IP is connected to the box
        :param ip: IP of the device you want to test
        :type ip: str
        :return: True is the device is connected, False if it's not
        :rtype: bool
        """
        all_devices = self.get_all_connected_devices()
        for device in all_devices:
            if ip == device['ipaddress']:
                return device['active'] == 1
        return False

    def conf_ip6(self, enable='1', ipadress=''):
        """
        Configure the IPv6 on the LAN
        Enable or disable the IPv6 on the LAN and configure the IPv6 interface ID.
        :param enable: Enable or disable IPv6 on the LAN.
        :ipadress New LAN IPv6 address 
        .. Todo :: Take in charge the ipadress
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PRIVATE,
                                  BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        self.bbox_url.set_api_name(BboxConstant.API_LAN, "ip6")
        data = {'enable': enable}
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_PUT, data,
                          self.bbox_auth)
        response = api.execute_api_request()
        if response.status_code == 200:
            print('ok')
        else:
            print(response.status_code)

    def get_lan_ip(self):
        """
        LAN - Get Bbox LAN IP Information
        This API returns ip configuration of the Bbox local Network.
        :rtype: object
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PRIVATE, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        self.bbox_url.set_api_name(BboxConstant.API_LAN, "ip")
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_GET, None,
                          self.bbox_auth)
        resp = api.execute_api_request()
        return resp.json()[0]['lan']

    """
    NAT PMP
    """

    def create_nat_rule(self,enable,description,protocol,ipaddress,internal_port,ipremote='',external_port=''):
        """
        NAT_PMP - Create a NAT-PMP rule
        Create a NAT-PMP rule.
        :param enable: 1=Enbable the rule
                       0=Disable the rule
        :type enable: int
        :param description: The description for this rule (up to 48 characters).
        :type description: str
        :param protocol: tcp = TCP only.
                        udp = UDP only.
                        esp = ESP only.
                        all = All of the above.
        :type  protocol: str
        :param ipadress: The local IP address where to forward packets.
        :type ipadress: str
        :param internal_port: The port where to forward packet.
        :type internal_port: str
        :param ipremote: (optional) The remote IP address where the packets are coming from.
                         When not set packets are forwarded from any source.
        :type ipremote: str
        :param external_port: (optinal) The external port where the packets are coming from.
                         When not set packets are forwarded from any port.
        :type external_port: str
        :return: True if HTTP status code = 201
        :rtype: bool
        """
        token = self.get_token()
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PRIVATE, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        url_suffix = "rules?btoken={}".format(token)
        data = {'enable': enable,'description': description,'protocol': protocol,'ipremote': ipremote,'external_port' : external_port, 'ipaddress': ipaddress,'internal_port':internal_port}
        self.bbox_url.set_api_name(BboxConstant.API_NAT, url_suffix)
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_POST, data,
                          self.bbox_auth)
        response = api.execute_api_request()
        if response.status_code == 201:
            return True
        else:
            return False

    def delete_nat_rule(self,id):
        """
        NAT_PMP - Delete a NAT-PMP rule
        Delete a NAT-PMP rule.
        :param id: Rule id to delete
        :type id: int
        :return: True if Http code is 200 or 202
        :rtypr: Bool
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PRIVATE, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        url_suffix = "rules/{}".format(id)
        self.bbox_url.set_api_name(BboxConstant.API_NAT, url_suffix)
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_DELETE, None,
                          self.bbox_auth)
        response = api.execute_api_request()
        if response.status_code == 200 or response.status_code == 202:
            return True
        else:
            return False

    def get_all_nat_rules(self):
        """
        NAT_PMP - Get all NAT-PMP rules
        Returns all existing NAT-PMP rules
        :rtype: object
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PRIVATE, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        self.bbox_url.set_api_name(BboxConstant.API_NAT, "rules")
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_GET, None,
                          self.bbox_auth)
        resp = api.execute_api_request()
        return resp.json()[0]['nat']


    """
    USER ACCOUNT
    """

    def login(self, password):
        """
        Authentify yourself against the box,
        :param password: Admin password of the box
        :type password: str
        :return: True if your auth is successful
        :rtype: bool
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PUBLIC, BboxConstant.AUTHENTICATION_LEVEL_PUBLIC)
        self.bbox_url.set_api_name("login", None)
        data = {'password': password}
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_POST, data,
                          self.bbox_auth)
        response = api.execute_api_request()
        if response.status_code == 200:
            self.bbox_auth.set_cookie_id(response.cookies["BBOX_ID"])
        return self.bbox_auth.is_authentified()

    def logout(self):
        """
        Destroy the auth session against the box
        :return: True if your logout is successful
        :rtype: bool
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PUBLIC, BboxConstant.AUTHENTICATION_LEVEL_PUBLIC)
        self.bbox_url.set_api_name("logout", None)
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_POST, None,
                          self.bbox_auth)
        response = api.execute_api_request()
        if response.status_code == 200:
            self.bbox_auth.set_cookie_id(None)
        return not self.bbox_auth.is_authentified()

    """
    WAN API
    """

    def get_xdsl_info(self):
        """
        Get all data about your xDSL connection
        :return: A dict with all data about your xdsl connection (see API doc)
        :rtype: dict
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PUBLIC, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        self.bbox_url.set_api_name(BboxConstant.API_WAN, "xdsl")
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_GET, None,
                          self.bbox_auth)
        resp = api.execute_api_request()
        return resp.json()[0]["wan"]["xdsl"]

    def get_xdsl_stats(self):
        """
        Get all stats about your xDSL connection
        :return: A dict with all stats about your xdsl connection (see API doc)
        :rtype: dict
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PUBLIC, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        self.bbox_url.set_api_name(BboxConstant.API_WAN, "xdsl/stats")
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_GET, None,
                          self.bbox_auth)
        resp = api.execute_api_request()
        return resp.json()[0]["wan"]["xdsl"]["stats"]

    def get_ip_stats(self):
        """
        Get all stats about your Wan ip connection
        :return: A dict with all stats about your Wan ip connection (see API doc)
        :rtype: dict
        """
        self.bbox_auth.set_access(BboxConstant.AUTHENTICATION_LEVEL_PUBLIC, BboxConstant.AUTHENTICATION_LEVEL_PRIVATE)
        self.bbox_url.set_api_name(BboxConstant.API_WAN, "ip/stats")
        api = BboxApiCall(self.bbox_url, BboxConstant.HTTP_METHOD_GET, None,
                          self.bbox_auth)
        resp = api.execute_api_request()
        return resp.json()[0]["wan"]["ip"]["stats"]

    def is_bbox_connected(self):
        """
        Check if your xDsl connection is ok
        :return: True is the box has an xdsl connection
        :rtype: bool
        """
        xdsl_info = self.get_xdsl_info()
        return xdsl_info["state"] == "Connected"

    def get_up_bitrates(self):
        """
        :return: the upload bitrates of the xdsl connectionbitrates in Mbps
        :rtype: float
        """
        xdsl_info = self.get_xdsl_info()
        return xdsl_info["up"]["bitrates"] / 1000

    def get_down_bitrates(self):
        """
        :return: the download bitrates of the xdsl connectionbitrates in Mbps
        :rtype: float
        """
        xdsl_info = self.get_xdsl_info()
        return xdsl_info["down"]["bitrates"] / 1000

    def get_up_used_bandwith(self):
        """
        Return a percentage of the current used xdsl upload bandwith
        Instant measure, can be very different from one call to another
        :return: 0 no bandwith is used, 100 all your bandwith is used
        :rtype: int
        """
        ip_stats_up = self.get_ip_stats()['tx']
        percent = ip_stats_up['bandwidth']*100/ip_stats_up['maxBandwidth']
        return int(percent)

    def get_down_used_bandwith(self):
        """
        Return a percentage of the current used xdsl download bandwith
        Instant measure, can be very different from one call to another
        :return: 0 no bandwith is used, 100 all your bandwith is used
        :rtype: int
        """
        ip_stats_up = self.get_ip_stats()['rx']
        percent = ip_stats_up['bandwidth']*100/ip_stats_up['maxBandwidth']
        return int(percent)
