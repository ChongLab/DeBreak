import time
import pysam

def genotype_filter_del(samfile,readpath,chrom,highcov):
	samfile=pysam.AlignmentFile(samfile,"rb")
	alldel=open(readpath,'r').read().split('\n')[:-1]
	filt='-gt'
	if chrom!='all':
		alldel=[c for c in alldel if c.split('\t')[0]==chrom]
		filt='-gt-'+chrom
	f=open(readpath+filt,'w')
	for c in alldel:
		chrom=c.split('\t')[0]
		start=int(c.split('\t')[1])
		stop=int(c.split('\t')[2])+start
		svsize=int(c.split('\t')[2])
		numsupp=int(c.split('\t')[3])
		#if numsupp > highcov:
			#f.write(c+'\tHighCov\n')
		#	continue
		leftcov=samfile.count(chrom,start-150,start-50)
		if leftcov>highcov*2:
			continue
		rightcov=samfile.count(chrom,stop+50,stop+150)
		if rightcov>highcov*2:
			continue
		localcov=max(leftcov,rightcov)
		'''
		if localcov > highcov:
			f.write(c+'\tHighCov\n')
		'''
		if localcov<=highcov:
			f.write(c+'\tPASS\n')
	f.close()
	return True

def genotype_del(samfile,readpath,chrom,highcov):
	samfile=pysam.AlignmentFile(samfile,"rb")
	alldel=open(readpath,'r').read().split('\n')[:-1]
	filt='-gt'
	if chrom!='all':
		alldel=[c for c in alldel if c.split('\t')[0]==chrom]
		filt='-gt-'+chrom
	
	f=open(readpath+filt,'w')
	for c in alldel:
		chrom=c.split('\t')[0]
		start=int(c.split('\t')[1])
		stop=int(c.split('\t')[2])+start
		svsize=int(c.split('\t')[2])
		numsupp=int(c.split('\t')[3])
		if numsupp > highcov:
			#f.write(c+'\tGT=1/0\tHighCov\n')
			continue
		leftcov=samfile.count(chrom,start-150,start-50)
		if leftcov>highcov*2:
			continue
		rightcov=samfile.count(chrom,stop+50,stop+150)
		if rightcov>highcov*2:
			continue

		localcov=max(leftcov,rightcov)
		
		'''	
		if localcov > highcov:			
			if numsupp>=0.6*localcov:
				f.write(c+'\tGT=1/1\tHighCov\n')
			if numsupp<0.6*localcov and numsupp>=0.2*localcov:
				f.write(c+'\tGT=1/0\tHighCov\n')
		'''
		if localcov<=highcov:
			if numsupp>=0.6*localcov:
				f.write(c+'\tGT=1/1\n')
			else:
				f.write(c+'\tGT=1/0\n')
		
	f.close()
	return True

def genotype_filter_ins(samfile,readpath,chrom,highcov):
	samfile=pysam.AlignmentFile(samfile,"rb")
	alldel=open(readpath,'r').read().split('\n')[:-1]
	filt='-gt'
	if chrom!='all':
		alldel=[c for c in alldel if c.split('\t')[0]==chrom]
		filt='-gt-'+chrom
	f=open(readpath+filt,'w')
	for c in alldel:
		chrom=c.split('\t')[0]
		start=int(c.split('\t')[1])
		numsupp=int(c.split('\t')[3])
		#if numsupp > highcov:
			#f.write(c+'\tHighCov\n')
		#	continue
		leftcov=samfile.count(chrom,start-150,start-50)
		if leftcov>highcov*2:
			continue
		rightcov=samfile.count(chrom,start+50,start+150)
		if rightcov>highcov*2:
			continue
		localcov=max(leftcov,rightcov)
		'''
		if localcov > highcov:
			f.write(c+'\tHighCov\n')
		'''
		if localcov<=highcov:
			f.write(c+'\tPASS\n')
	f.close()
	return True

def genotype_ins(samfile,readpath,chrom,highcov):
	samfile=pysam.AlignmentFile(samfile,"rb")
	alldel=open(readpath,'r').read().split('\n')[:-1]	
	filt='-gt'
	if chrom!='all':
		alldel=[c for c in alldel if c.split('\t')[0]==chrom]
		filt='-gt-'+chrom
	f=open(readpath+filt,'w')

	for c in alldel:

		chrom=c.split('\t')[0]
		start=int(c.split('\t')[1])
		numsupp=int(c.split('\t')[3])
		svsize=c.split('\t')[2]
		if numsupp > highcov:
			#f.write(c+'\tGT=0/1\tHighCov\n')
			continue
		leftcov=samfile.count(chrom,start-150,start-50)
		if leftcov>highcov*2:
			continue
		rightcov=samfile.count(chrom,start+50,start+150)
		if rightcov>highcov*2:
			continue
		localcov=max(leftcov,rightcov)
		'''
		if localcov<=highcov:
			f.write(chrom+'\t'+str(start)+'\t'+str(svsize)+'\t'+str(numsupp)+'\t'+str(localcov)+'\n')
		
		if localcov > highcov:
			if numsupp>=0.6*localcov:
				f.write(c+'\tGT=1/1\tHighCov\n')
			if numsupp<0.6*localcov and numsupp>=0.2*localcov:
				f.write(c+'\tGT=1/0\tHighCov\n')
		'''

		if localcov<=highcov:
			if numsupp>=0.6*localcov:
				f.write(c+'\tGT=1/1\n')
				continue

			allalignment=samfile.fetch(chrom,start-1,start+1)
			numsupp2=0
			localcov2=0
			for align in allalignment:
				if align.flag!=0:
					continue
				if int(svsize)<500 and abs(align.reference_start-start)<=100 or abs(start-align.reference_end)<=100:
					continue
				localcov2+=1
				cigar=align.cigartuples
				readstart=align.reference_start
				readlen=0


				for pair in cigar:
					if pair[0] in [0,2]:
						readlen+=pair[1]; continue
					if pair[0] == 1:
						if 0.7<=pair[1]/float(svsize)<=1.43 and abs(readstart+readlen-start)<=500:
							numsupp2+=1; break
				if int(svsize)>=500:
					if abs(readstart-start)<=250 and cigar[0][0] in [4,5]:
						numsupp2+=1; continue
					if abs(start-align.reference_end)<=250 and cigar[-1][0] in [4,5]:
						numsupp2+=1


		if localcov<= highcov  and localcov2<=highcov:
			if numsupp2>=0.6*localcov2:
				f.write(c+'\tGT=1/1\n')
			else:
				f.write(c+'\tGT=1/0\n')
		
	f.close()
	return True

def genotype_filter_tra(samfile,readpath,chrom,highcov):
	samfile=pysam.AlignmentFile(samfile,"rb")
	alldel=open(readpath,'r').read().split('\n')[:-1]
	filt='-gt'
	if chrom!='all':
		filt='-gt-'+chrom
		alldel=[c for c in alldel if c.split('\t')[0]==chrom]
	f=open(readpath+filt,'w')
	for c in alldel:
		chr1=c.split('\t')[0]
		bp1=int(c.split('\t')[1])
		chr2=c.split('\t')[2]
		bp2=int(c.split('\t')[3])
		supp=int(c.split('\t')[4])
		#if supp >highcov:
			#f.write(c+'\tHighCov\n')
		#	continue
		leftcov1=samfile.count(chr1,bp1-150,bp1-50)
		if leftcov1>highcov*2:
			continue
		rightcov1=samfile.count(chr1,bp1+50,bp1+150)
		if rightcov1>2*highcov:
			continue
		leftcov2=samfile.count(chr2,bp2-150,bp2-50)
		if leftcov2>2*highcov:
			continue
		rightcov2=samfile.count(chr2,bp2+50,bp2+150)
		if rightcov2>2*highcov:
			continue
		local_cov=max(leftcov1,rightcov1,leftcov2,rightcov2)
		'''
		if local_cov>highcov:
			f.write(c+'\tHighCov\n')
		'''
		if local_cov<=highcov:
			f.write(c+'\tPASS\n')
	f.close()
	return True

def genotype_tra(samfile,readpath,chrom,highcov):
	samfile=pysam.AlignmentFile(samfile,"rb")
	alldel=open(readpath,'r').read().split('\n')[:-1]
	filt='-gt'
	if chrom!='all':
		alldel=[c for c in alldel if c.split('\t')[0]==chrom]
		filt='-gt-'+chrom
	f=open(readpath+filt,'w')
	for c in alldel:
		chr1=c.split('\t')[0]
		bp1=int(c.split('\t')[1])
		chr2=c.split('\t')[2]
		bp2=int(c.split('\t')[3])
		supp=int(c.split('\t')[4])
		if supp >highcov:
			#f.write(c+'\tGT=1/0HighCov\n')
			continue
		leftcov=samfile.count(chr1,bp1-150,bp1-50)
		if leftcov>2*highcov:
			continue
		rightcov=samfile.count(chr1,bp1+50,bp1+150)
		if rightcov>2*highcov:
			continue
		local_cov=max(rightcov,leftcov)

		leftcov=samfile.count(chr2,bp2-150,bp2-50)
		if leftcov>2*highcov:
			continue
		rightcov=samfile.count(chr2,bp2+50,bp2+150)
		if rightcov>2*highcov:
			continue
		local_cov=max(local_cov,rightcov,leftcov)
		filt=''
		'''
		if local_cov>highcov:
			filt='\tHighCov'
		'''
		if local_cov<=highcov:
			if supp>=0.6*local_cov:
				f.write(c+'\tGT=1/1'+filt+'\n')
			else:
				f.write(c+'\tGT=1/0'+filt+'\n')
		
	return True

if __name__ =="__main__":
	#readpath='/data/scratch/maggic/HG002/pacbio/debreak_ccs_merge/new1.75cutoff/'
	#samfile='/data/scratch/maggic/HG002/pacbio/ccs_merge/merged.sort.bam'

	##readpath='/data/scratch/maggic/HG00514/debreak/'
	#samfile='/data/scratch/maggic/HG00514/minimap2/merged.sort.bam'
	readpath='/data/scratch/maggic/HG002/pacbio/debreak_mt_minimap2_215/test_compound_9.18_wholedebreak/'
	samfile='/data/scratch/maggic/HG002/pacbio/alignment_mt_minimap2_215/merged.sort.bam'

	highcov=150
	t1=time.time()
	#genotype_del(samfile,readpath+'deletion-merged','all',highcov,)
	t2=time.time()
	print t2-t1
	genotype_ins(samfile,readpath+'insertion-merged','all',highcov,)
	t3=time.time()
	#print t3-t2
	'''
	genotype_del(samfile,readpath+'duplication-merged-new','all',highcov,)
	t4=time.time()
	print t4-t3
	genotype_del(samfile,readpath+'inversion-merged-new','all',highcov,)
	t5=time.time()
	print t5-t4
	
	t5=time.time()

	genotype_tra(samfile,readpath+'translocation-merged-new','all',highcov,)
	t6=time.time()
	print t6-t5
	'''
