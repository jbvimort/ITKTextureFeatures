import itk, sys, json, os, re


#Looking for all the cases contained in the file

class case(object):
    def __init__(self, ID):
        self.caseID = ID
        self.scanFilePath = None
        self.segmentationFilePath = None
        self.outputFilePath = None
        self.GLCMFeatures = None
        self.GLRLMFeatures = None

caseDict = {}
inputDirectory = sys.argv[1]
outputDirectory = sys.argv[2]

for fileName in os.listdir(inputDirectory):
    if fileName.endswith(".nrrd"):
        print(fileName)
        if fileName.startswith("SegmC"):
            caseID = re.search("SegmC(.+?).nrrd", fileName).group(1)
            if caseID in caseDict:
                caseDict[caseID].segmentationFilePath = os.path.join(inputDirectory, fileName)
            else:
                temp = case(caseID)
                temp.segmentationFilePath = os.path.join(inputDirectory, fileName)
                caseDict[caseID] = temp
        elif fileName.startswith("Scan"):
            caseID = re.search("Scan(.+?).nrrd", fileName).group(1)
            if caseID in caseDict:
                caseDict[caseID].scanFilePath = os.path.join(inputDirectory, fileName)
            else:
                temp = case(caseID)
                temp.scanFilePath = os.path.join(inputDirectory, fileName)
                caseDict[caseID] = temp

for case in caseDict.values():
    im = itk.imread(case.scanFilePath)
    mask = itk.imread(case.segmentationFilePath)
    filtr = itk.CoocurrenceTextureFeaturesImageFilter.ISS3VIF3.New(im)
    filtr.SetNumberOfBinsPerAxis(10)
    filtr.SetMaskImage(mask)
    filtr.SetPixelValueMinMax(int(sys.argv[3]), int(sys.argv[4]))
    filtr.SetNeighborhoodRadius(int(sys.argv[5]))
    result = filtr.GetOutput()
    result.Update()

    npMask = itk.GetArrayFromImage(mask)
    npResult = itk.GetArrayFromImage(result)

    Xmax = npResult.shape[0]
    Ymax = npResult.shape[1]
    Zmax = npResult.shape[2]

    dict = {}

    for i in range(Xmax):
        for j in range(Xmax):
            for k in range(Xmax):
                if i == j == k == 15:
                    if npMask[i,j,k] == 1:
                        print "###"
                        print i
                        print j
                        print k
                        dict[str(i) + ";" + str(j) + ";" + str(k)] = npResult[i,j,k].tolist()


    with open( os.path.join(outputDirectory , case.caseID + ".txt"), 'w') as outfile:
        json.dump(dict, outfile)

