
Basic python module to be used on other components: PSAM, NED, SPM


Just install dependencies and copy psarClient.py where you need it.

	pip install -r requirements.txt
	cp psarClient.py YOUR_DIRECTORY

To use it, import psarClient.py into your file and create a Client object

	import psarClient
	client=psarClient.Client('http://PSAR_IP:PSAR_PORT')
	
If you are using authentication, the first thing you must do is to get a service token:
	
	token=client.get_token(user,password,tenant,auth_URL)

(If you are not sure what your auth_URL is, then it's probably http://PSAR_IP:5000/v2.0)	

Then use the token when you use the client's methods, e.g

	r=client.get_status(token=token)

When using the client as a CLI command, there is a default URL in the code, but a custom one can be specified using the --url option with following format: --url='http://PSAR_IP:PSAR_PORT'

Typical use cases:

*	Downloading an image
	
	*	Using python class:
	
		from psarClient import Client
		client=psarClient.Client('http://PSAR_IP:PSAR_PORT')
		client.get_image_file('PSA_ID','path/to/save/the/image')
	
	*	As a CLI command:

		./psarClient.py image download 'PSA_ID' 'path/to/save/the/image'

*       Uploading an image

        *       Using python class:

                from psarClient import Client
                client=psarClient.Client('http://PSAR_IP:PSAR_PORT')
                client.put_image_file('PSA_ID','path/of/the/image')

        *       As a CLI command:

               	./psarClient.py image upload 'PSA_ID' 'path/of/the/image'



*       Downloading a manifest

        *       Using python class:

                from psarClient import Client
                client=psarClient.Client('http://PSAR_IP:PSAR_PORT')
                client.get_manifest('PSA_ID','path/to/save/the/manifest')

        *       As a CLI command:

                ./psarClient.py manifest download 'PSA_ID' 'path/to/save/the/manifest'




*       Uploading a manifest

        *       Using python class:

                from psarClient import Client
                client=psarClient.Client('http://PSAR_IP:PSAR_PORT')
                client.put_manifest_file('PSA_ID','path/of/the/manifest')

        *       As a CLI command:

                ./psarClient.py manifest upload 'PSA_ID' 'path/of/the/manifest'


*       Downloading a plugin

        *       Using python class:

                from psarClient import Client
                client=psarClient.Client('http://PSAR_IP:PSAR_PORT')
                client.get_plugin_file('PSA_ID','path/to/save/the/plugin')

        *       As a CLI command:

                ./psarClient.py plugin download 'PSA_ID' 'path/to/save/the/plugin'

*       Uploading a plugin

        *       Using python class:

                from psarClient import Client
                client=psarClient.Client('http://PSAR_IP:PSAR_PORT')
                client.put_plugin_file('PSA_ID','path/of/the/plugin')

        *       As a CLI command:

                ./psarClient.py plugin upload 'PSA_ID' 'path/of/the/plugin'

psam_client.py
==============
 
Another new tool is included to be used for on-boarding PSAs. This tool group several actions done by psarClient.py:
 Registering a new PSA and uploading all its elements (image, manifest and plugin).
 
To use it, create a new directory and place in it the image, manifest and plugin of your PSA, with exactly these names 'image','manifest' and 'plugin' respectively, and run the program like this:
 
       psam_client.py create --url=PSAR_URL <psa_id> <directory you just created>
 
You can use de '--url' argument or set the PSAR_URL environment variable.



