Main release file is update_simulator_release.bat
This calls 3 .bat files in this order:

	make_html.bat
		Read all markdown comments in code and create an html site with it.

	make_simulator_exe_file.bat
		Package code into an exe file.

	copy_to_server.bat
		Copy the exe file, all config files, spreadsheets folder, and graphics folder to server.


