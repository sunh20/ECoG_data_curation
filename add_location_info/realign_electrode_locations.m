Rootpath = '/home/stepeter/Documents/realign_electrode_locs/data/';
%%
addpath('/home/stepeter/Documents/fieldtrip-20181206/');
% krang_ID = '294e1c';
useEllipse = 0;
all_files = dir([Rootpath '*_MNIcoords.txt']);
disp(length(all_files));
% krang_IDs = {'cdceeb', 'ecb43e', '69da36', 'b3719b', '294e1c', '0b5a2e', '0a80cf', 'c5a5e9', 'fca96e', '3f2113', 'acabb1', 'c19968', '13d2d8'};
for i = 1:length(all_files) %1:length(krang_IDs)
    if exist([Rootpath all_files(i).name(1:(end-4)) '_realigned.txt'],'file')==0
        disp(all_files(i).name)
        elec = importdata([Rootpath all_files(i).name]); %[Rootpath krang_IDs{i} '_Trodes_MNIcoords.txt']);
        if useEllipse==0
            posIndsX = find(elec(:,1)>0);
            elec(posIndsX,1) = -elec(posIndsX,1);
        end
        elec_orig.chanpos = elec(:,:);
        elec_orig.elecpos = elec(:,:);
        elec_orig.units = 'mm';
        elec_orig.label = sprintfc('%d',1:size(elec,1))';
        elec_orig.chantype = cell(size(elec,1),1); elec_orig.chantype(:) = {'eeg'};
        elec_orig.chanunit = cell(size(elec,1),1); elec_orig.chanunit(:) = {'V'};
        elec_orig.coordsys = 'mni';
        %Set cfg parameters
        cfg=[];
        cfg.method = 'headshape';
        cfg.warp = 'dykstra2012';
        if useEllipse==1
            cfg.headshape = [Rootpath 'mni_head_pnts_ellips.mat'];
        else
            cfg.headshape = [Rootpath 'mni_head_pnts_hires.mat'];
        end

        elec_realigned = ft_electroderealign(cfg,elec_orig);
        if useEllipse==1
            fname_out = [Rootpath all_files(i).name(1:(end-4)) '_realigned_ellips.txt']; %[Rootpath krang_IDs{i} '_realigned_ellips_Trodes_MNIcoords.txt'];
        else
            fname_out = [Rootpath all_files(i).name(1:(end-4)) '_realigned.txt']; %[Rootpath krang_IDs{i} '_realigned_Trodes_MNIcoords.txt'];
            elec_realigned.chanpos(posIndsX,1) = -elec_realigned.chanpos(posIndsX,1);
        end
        dlmwrite(fname_out,elec_realigned.chanpos,',')
    end
end
%%
% figure; hold on; scatter3(elec_orig.chanpos(1:(end-8),1),elec_orig.chanpos(1:(end-8),2),elec_orig.chanpos(1:(end-8),3));
% scatter3(elec_realigned.chanpos(1:(end-8),1),elec_realigned.chanpos(1:(end-8),2),elec_realigned.chanpos(1:(end-8),3),'r'); hold off;
