function ipcam
% IPCAM i
% click one of the plot-type push buttons. Clicking the button
% plots the selected data in the axes.
 
   %  Create and then hide the GUI as it is being constructed.
   %f = figure('Visible','off','Position',[360,500,450,285]);
   f = figure('Visible','off','Position',[360,500,850,400]);
 
   %  Construct the components.
   hpopup = uicontrol('Style','popupmenu',...
          'String',{'Peaks','Membrane','Sinc'},...
          'Position',[700,350,100,25],...
          'Callback',@popup_menu_Callback);
   hconnect = uicontrol('Style','pushbutton','String','Connect',...
          'Position',[715,300,70,25],...
          'Callback',@connectbutton_Callback);
   
   hlog = uicontrol('Style','pushbutton',...
          'String','Save Log',...
          'Position',[715,135,70,25],...
          'Callback',@logbutton_Callback); 
   hfps = uicontrol('Style','text','String','fps',...
          'Position',[725,90,60,15]);
   hsize = uicontrol('Style','text','String','fps',...
          'Position',[725,70,60,15]);
   
   ha = axes('Units','Pixels','Position',[50,60,320,240]); 
   align([hconnect,hlog,hfps,hsize,hpopup],'Center','None');
   
   firstTime = 1;
   fileLOG = [];
   
   s = instrhwinfo('serial');
   hpopup.String = s.SerialPorts;
 
   
   % Initialize the GUI.
   % Change units to normalized so components resize 
   % automatically.
   f.Units = 'normalized';
   ha.Units = 'normalized';
   hconnect.Units = 'normalized';
   hlog.Units = 'normalized';
   hfps.Units = 'normalized';
   hsize.Units = 'normalized';
   hpopup.Units = 'normalized';
   
   %Create a plot in the axes.

   % Assign the GUI a name to appear in the window title.
   f.Name = 'Alter-Info: IPCAM';
   % Move the GUI to the center of the screen.
   movegui(f,'center')
   % Make the GUI visible.
   f.Visible = 'on';
   f.CloseRequestFcn = @CloseFigureFunction;
   
   t = timer('TimerFcn',@timer_callback,'ExecutionMode','fixedRate');

    SerialObject =[];%  serial('/dev/tty.usbmodemFD123','BaudRate',1843200); %/dev/tty.usbmodemfa131'
    state = 'disconnected'; 
    receivedImages = 0;
    imageSize = 0;
   
   %  Callbacks for simple_gui. These callbacks automatically
   %  have access to component handles and initialized data 
   %  because they are nested at a lower level.
 
   
   
   
    function timer_callback(source,eventdata)
        persistent number
        fps = receivedImages - number;
        hfps.String = [num2str(fps,'%d'),' fps'];
        number = receivedImages;
        mean(imageSize)/1000
        hsize.String = [num2str(mean(imageSize)/1000,'%03.1f'),' kB'];
        imageSize = [];
    end
   
   %  Pop-up menu callback. Read the pop-up menu Value property
   %  to determine which item is currently displayed and make it
   %  the current data.
      function popup_menu_Callback(source,eventdata)
          s = instrhwinfo('serial');
         hpopup.String = s.SerialPorts;
         % Determine the selected data set.
         str = source.String;
         val = source.Value;
         
         SerialObject = serial(str{val},'BaudRate',1843200);
         set(SerialObject,'InputBufferSize', 1000000);
        SerialObject.BytesAvailableFcnMode = 'byte'; % 
        SerialObject.BytesAvailableFcnCount = 5000; % 
        SerialObject.BytesAvailableFcn = @SerialObject_Callback;

      end
  
  %% Serial Port Callback 
    function SerialObject_Callback(source,eventdata) 
        persistent data i image tail head j state_scan 
        if firstTime 
            image = zeros(1,60000);
            state_scan = 0;
            firstTime = 0;
            data = [];       
        end
        n = 0;
        while n < 1000
            n = get(SerialObject,'BytesAvailable');
        end
        [datanew, count] = fscanf(SerialObject,'%c',n);
        data = [data datanew];
        if strcmp(hlog.String,'Stop Log')
            fwrite(fileLOG,data ,'uint8');
        end
        MAX_SIZE_IMAGE = 60000;
        num_array = uint8(data);
        N = length(num_array);
        i = 1;
        head = 1;
        
        while( i <= N - 1)
            switch (state_scan)
                case 0
                    if( num_array(i)==255 && num_array(i+1)==216)
                        image = zeros(1,MAX_SIZE_IMAGE);
                        head = i;
                        state_scan = 1; 
                        j = 1;
                        image(j) = data(head);               
                    end          
                case 1
                    j = j + 1;
                    image(j)= data(i);
                    if( num_array(i)==255 && num_array(i+1)==217 )
                        tail = i+1;
                        state_scan = 2; 
                    end
                case 2
                    j = j + 1;
                    image(j)= data(i);
                    img = decodeJpeg(image(1:j));
                    imageSize = [imageSize j];
                    gca;
                    imshow(img);
                    drawnow
                    state_scan = 0; 
                    receivedImages = receivedImages + 1;
                otherwise
            end 
            i = i + 1;
        end
        data = data(N);
        
      end
   % Push button callbacks. Each callback plots current_data in
   % the specified plot type.
%% Close Request Function
    function [] = CloseFigureFunction(source,eventdata) 
        switch state  
            case 'disconnected'
           
            case 'connected'
                fclose(SerialObject);
                disp(['Com Port Status: ',SerialObject.status])
            otherwise
        end         
         disp('ipcam closed');
         delete(SerialObject)
         clear SerialObject
         delete(gcf);     
    end

   %% Connect/Disconnect Button Callback
   function connectbutton_Callback(source,eventdata) 

      
    switch state  
        case 'disconnected'
            % Open the serial port   
            fopen(SerialObject);
            disp(['Com Port Status: ',SerialObject.status])
            flushinput(SerialObject)
            state = 'connected'; 
            hconnect.String = 'disconnect';
            hpopup.Enable = 'off';
            firstTime = 1;
            start(t);
        case 'connected'
            % Close Port
            fclose(SerialObject);
            disp(['Com Port Status: ',SerialObject.status])
            state = 'disconnected';
            hconnect.String = 'connect';
            hpopup.Enable = 'on';
            stop(t);
        otherwise
    end
   end
%% %% Close Port
   function closebutton_Callback(source,eventdata) 
      % Close Port

    fclose(SerialObject);
    display(['Com Port Status: ',SerialObject.status])


   end
%% Save/Stop Log button 
   function logbutton_Callback(source,eventdata)
        str = hlog.String;
        switch str
            case 'Save Log'
                hlog.String = 'Stop Log';
                fileLOG = fopen('log.txt','w');
            case 'Stop Log'
                hlog.String = 'Save Log';
                fclose(fileLOG);
            otherwise
                %hlog.String = 'Stop Log';
        end
   end 
 
end 