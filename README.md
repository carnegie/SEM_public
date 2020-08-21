# SEM-1.1
Python 3.6 version of SEM-1. This is a Simple Energy Model that optimizes electricity (or electricity
and fuels) without considering any spatial variation, policy, capacity markets, etc.

<br>
<b>=====  WISH LIST OF THINGS TO BE DONE ON THIS MODEL  =====</b>
<br>

The following is a wish list for improvements to our model and its usability:

A. Some LIFO storage and PGP_storage analysis and figures as part of standard output.

B. Reconfigure model to allow running more cases without needing more memory.

C. Automate some checks on aberrant usage of storage (?)

D. Make version with specified capacities.

E. Add inter-case comparisons to Quick_Look.py

F. Do a runtime analysis to speed up execution of Quick_Look.py

G. Make version that can be spread across CEES-Mazama.

<br>
<b>=====  WINDOWS 10 INSTALLATION INSTRUCTIONS  ===== </b>
<br>
The following is installation instructions for Windows 10 machines.

1. Use remove programs to remove all python2.x programs. This uninstalls Anaconda2.

2. Use remove programs to remove all Gurobi (Not sure this is necessary. I had Gurobi 7 and new release is Gurobi 8.)

3. Install Anaconda3. https://www.anaconda.com/download/ https://conda.io/docs/user-guide/install/windows.html

4. Install Visual C++ 14.0.  Download and install software using this link. https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=15 See this link for more information: https://www.scivision.co/python-windows-visual-c++-14-required/

5. Download and install Gurobi. http://www.gurobi.com/documentation/8.0/quickstart_windows/quickstart_windows.html http://www.gurobi.com/documentation/8.0/quickstart_windows/creating_a_new_academic_li.html#subsection:createacademiclicense

6. Activate Gurobi license. You have to go to this page https://user.gurobi.com/download/licenses/current to see what licenses are allocated to you. Click on the license that will pertain to your machine. A window will open up that will have some text like:

		grbgetkey 2c8c6fa0-ad45-11e8-a2c6-0acd5117eeae

Copy that text and paste in in an Anaconda window. (You might start these Anaconda windows as Administrator just to be on the safe side.)

7. Set up python link to Gurobi. Open up the Anaconda3 window as Administrator from the start menu.(Note this is a dos window, not a linux window.) And then type:

	       > cd  /c/gurobi801/win64
	       > python setup.py install

8. Install cvxpy, version 0.4.11. For python3, cvxpy must be installed with pip. They recommend making a special virtual environment to allow different versions of things to run on the same machine, but I just installed into my general space.  Open up an Anaconda window (I did it as Administrator) and type

		> pip install cvxpy==0.4.11 

If this install fails on installing the ecos package, try the following line in an Anaconda window:

                > conda install ecos
		> pip install cvxpy==0.4.11

<b>Additional notes on installing cvxpy</b> (Mengyao)

If you get error messages for not having (or having the correct versions of) ecos, scs, or cvxcanon, try the following command (<a href="https://anaconda.org/sebp/cvxpy">Anaconda Cloud</a>): 

                > conda install -c sebp cvxpy==0.4.11

This command should automatically download / install the right packages needed for cvxpy ("-c CHANNEL" specifies additional channels to search for packages; sebp is a contributer on Anaconda Cloud).

Check the installation with

		> nosetests cvxpy 

9. Download and run python3 version of the Simple Energy Model -- SEM-1.1: https://github.com/ClabEnergyProject/SEM-1.1
-- Open case_input.xlsx in excel. Make the cases you want (by altering base case or ratios to base case), and then save sheet as case_input.csv.
-- Open Spyder and then within Spyder navigate to the folder that was cloned from github and open and run Simple_Energy_Model.py


<br>
<b>=====  MacOS 10.13 INSTALLATION INSTRUCTIONS  ===== </b>
<br>
The following is installation instructions for MacOS 10.13 machines.

1. If you installed Anaconda2 before, use remove programs to remove Anaconda2. You don't need to remove default python2 which might cause unexpected error 

2. Use remove programs to remove all Gurobi. Also, delete Gurobi license (normally under "/Users/$username/" if you didn't specify any location when installing) 

3. Install Anaconda3 for MacOS. https://www.anaconda.com/download/ 

4. Download and install Gurobi. http://www.gurobi.com/downloads/download-center  http://www.gurobi.com/downloads/gurobi-optimizer 

5. Activate Gurobi license. You have to go to this page https://user.gurobi.com/download/licenses/current to see what licenses are allocated to you. Click on the license that will pertain to your machine. A window will open up that will have some text like:  

	grbgetkey 2c8c6fa0-ad45-11e8-a2c6-0acd5117eeae

6. Copy that text and paste it in an Anaconda terminal window. (You might start these Anaconda windows as Administrator just to be on the safe side.)

7. Set up python link to Gurobi. Open up the Anaconda3 terminal window as Administrator from the start menu. And then type: 

	> conda config --add channels http://conda.anaconda.org/gurobi
	
	> conda install gurobi

8. Install cvxpy, version 0.4.11. For python3, cvxpy must be installed with pip. Open up an Anaconda window (I did it as Administrator) and type  

	> pip install cvxpy==0.4.11 

9. If you get error messages for not having (or having the correct versions of) ecos, scs, or cvxcanon, try the following command (Anaconda Cloud):

	> conda install -c sebp cvxpy==0.4.11

This command should automatically download / install the right packages needed for cvxpy ("-c CHANNEL" specifies additional channels to search for packages; sebp is a contributer on Anaconda Cloud).

10. Check the installation with

	> nosetests cvxpy 

If you did not remove old Gurobi license and installed a new one, you might see error in this step. You need to delete the old Gurobi licencse and install the new one for your current Gurobi version

11. Download and run python3 version of the Simple Energy Model -- SEM-1.1: https://github.com/ClabEnergyProject/SEM-1.1 -- Open case_input.xlsx in excel. Make the cases you want (by altering base case or ratios to base case), and then save sheet as case_input.csv. -- Open Spyder and then within Spyder navigate to the folder that was cloned from github and open and run Simple_Energy_Model.py
