#!/bin/bash

#select random server from our list of config files
shopt -s globstar failglob
if servers=(/path/to/vpn/configs/**.ovpn); then
	#grabs a random config file from our directory
	server="${servers[RANDOM % ${#servers[@]}]}"
fi

# check if the tunnel already exists before trying to create it
proc=$(ps aux | grep openvpn | grep .ovpn)
if [ "$proc" == "" ]; then
  echo "Creating Tunnel"
else
  echo "Tunnel Exists: ($proc)"
  exit 0
fi

#spawn openvpn and pass our creds.
if [[ -n $server ]]; then
	expect <<END
	spawn openvpn "$server"
	expect "Enter Auth Username:" {
		send "ENTER_USERNAME\n"
	}

	expect "Enter Auth Password:" {
		send "ENTER_PASSWORD\n"
	}
	expect eof	
	interact
END

fi
