# coding: utf-8
# Written by Wendo Sabée
# Manages local settings. SETTINGS ARE NOT SAVED LOCALLY BETWEEN SESSIONS (for now)!

import os
import ast

# Setup logger
import logging
_logger = logging.getLogger(__name__)

from Tribler.Category.Category import Category

from DownloadManager import DownloadManager
from BaseManager import BaseManager

ENVIRONMENT_SETTINGS_PREFIX = "TRIBLER_SETTING_"


class SettingsManager(BaseManager):
    def _connect(self):
        """
        Load settings from environment variables.
        :return: Nothing.
        """
        if not self._connected:
            self._connected = True

            self._load_settings_from_env()
        else:
            raise RuntimeError('SettingsManager already connected')

    def _xmlrpc_register(self, xmlrpc):
        """
        Register the public functions in this manager with an XML-RPC Manager.
        :param xmlrpc: The XML-RPC Manager it should register to.
        :return: Nothing.
        """
        xmlrpc.register_function(self.get_thumbs_directory, "settings.get_thumbs_directory")
        xmlrpc.register_function(self.get_family_filter, "settings.get_family_filter")
        xmlrpc.register_function(self.set_family_filter, "settings.set_family_filter")
        xmlrpc.register_function(self.set_max_download, "settings.set_max_download")
        xmlrpc.register_function(self.get_max_download, "settings.get_max_download")
        xmlrpc.register_function(self.set_max_download, "settings.set_max_upload")
        xmlrpc.register_function(self.get_max_download, "settings.get_max_upload")

    def _load_settings_from_env(self):
        """
        Settings are passed to the Tribler process on startup with the TRIBLER_SETTING_* environment variables. This
        function iterates over the environment variables and calls the setter functions associated with any found
        variables.
        :return: Nothing.
        """
        def get_value(value):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            else:
                return ast.literal_eval(value)

        for envkey in os.environ.keys():
            if envkey.startswith(ENVIRONMENT_SETTINGS_PREFIX):
                try:
                    function_name = "set_%s" % envkey[len(ENVIRONMENT_SETTINGS_PREFIX):].lower()
                    function_value = os.environ[envkey]
                    _logger.info("Setting preset setting with %s(%s)" % (function_name, function_value))

                    # Call setter
                    getattr(self, function_name)(get_value(function_value))
                except Exception, e:
                    _logger.warn("Could not set settings for key %s: %s" % (envkey, e.args))

    def get_thumbs_directory(self):
        """
        Returns the collected_torrent_files directory that contains the folders containing collected thumbnail data.
        These folders have the format of .../collected_torrent_files/thumbs-[INFOHASH]/[CONTENTHASH]/, where [INFOHASH]
        is the infohash of the torrent file, and [CONTENTHASH] a hash belonging to the thumbnail torrent. Each of these
        folders has one of multiple image files that can be used as thumbnails.
        :return: Path to collected_torrent_files directory.
        """
        return self._session.get_torrent_collecting_dir()

    def get_family_filter(self):
        """
        Get the current state of the family filter.
        :return: Boolean indicating state.
        """
        catobj = Category.getInstance()
        return catobj.family_filter_enabled()

    def set_family_filter(self, enable):
        """
        Set the state of the family filter.
        :param enable: Boolean with the new state.
        :return: Boolean indicating success.
        """
        try:
            Category.getInstance().set_family_filter(enable)
            return True
        except:
            return False

    def set_max_download(self, speed):
        """
        Sets the maximum download speed in the rate limiter.
        :param speed: The maximum speed in KiB/s
        :return: Boolean indicating success.
        """
        try:
            DownloadManager.getInstance().set_max_download(speed)
            return True
        except:
            return False

    def get_max_download(self):
        """
        Gets the maximum download speed from the rate limiter
        :return: Maximum download speed in KiB/s
        """
        try:
            return DownloadManager.getInstance().get_max_download()
        except:
            return False

    def set_max_upload(self, speed):
        """
        Sets the maximum upload speed in the rate limiter.
        :param speed: The maximum speed in KiB/s
        :return: Boolean indicating success.
        """
        try:
            DownloadManager.getInstance().set_max_upload(speed)
            return True
        except:
            return False

    def get_max_upload(self):
        """
        Gets the maximum upload speed from the rate limiter
        :return: Maximum upload speed in KiB/s
        """
        try:
            return DownloadManager.getInstance().get_max_upload()
        except:
            return False