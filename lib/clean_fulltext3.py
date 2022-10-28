import re

def add_to_list(line_pair, line_pairs, del_line_pairs):
    responsetext = ''
    if not line_pair.strip():
        return responsetext
    if line_pair in line_pairs:
        # will be deleted later
        if not line_pair in del_line_pairs:
            del_line_pairs.append(line_pair)
            responsetext = 'DD %s' % re.sub('\n','\\n',line_pair)
    else:
        line_pairs.append(line_pair)
    return responsetext
    
def clean_fulltext_moriond(inlines):        
    fulltext = ''
    for line in inlines:
        line = line.strip()
        line = re.sub(r'^(\d{1,2})\. ', r'[\1] ', line)
        fulltext = '%s%s\n' % (fulltext, line)
            
    return fulltext

def clean_fulltext_jacow(inlines, pairmode=True, verbose=3):
    """ 
    Delete content from Header and Footer of JACoW articles from fulltext:
    JACoW Publishing
    DOI, ISBN
    Name of Conference
    License
    Article-ID & page-number
    Session title 
    
    @param inlines: fulltext as list of strings / lines
    @param pairmode: boolean - to turn off search for frequent pairs of lines (e.g. session titles)
    @param verbose: verbose > 5 gets chatty
    @return: fulltext as string
    """
    import re
    
    outtext = []
    del_lines = []
    line_pairs = []
    del_line_pairs = []
    
    doi = None
    artid = None
    skipline = 0
    sessionline = 0

    for line in inlines:
        if skipline > 0:
            # don't add this line to fulltext
            skipline += -1
            if verbose > 5:
                print('S %s' % line)
            continue

        line = line.strip()

        if sessionline > 0:
            # add this line to line_pairs
            responsetext = add_to_list(line, line_pairs, del_line_pairs)
            if responsetext and verbose > 5:
                print(responsetext)
            sessionline += -1
            
        if not doi:
            # collect everything up and incl. DOI in del_lines - this is repeated in the header
            if line:
                del_lines.append(line)
            if line.startswith('doi:10.18429/JACoW'):
                # get the article-id from the DOI
                doi = line[4:]
                artid = doi.split('-')[-1]
        else:
            if line == artid:
                # skip this line and next, which is the page-number
                # the next two lines are candidates for session titles
                if verbose > 5:
                    print('A %s' % line)
                skipline = 1
                sessionline = 2
                continue
            if line in del_lines:
                # this is known garbage from header / footer
                if verbose > 5:
                    print('D %s' % line)
                continue
        
            if line.startswith('Content from this work may be used under the terms of the CC BY'):
                # add license to del_lines 
                del_lines.append(line)
                if verbose > 5:
                    print('C %s' % line)
                continue
            if line.startswith('ISBN: '):
                # hopefully no other lines start with 'ISBN: '
                prev_line = outtext.pop() # the previous line is the conference Name
                del_lines.append(line)
                del_lines.append(prev_line)
                if verbose > 5:
                    print('I %s' % prev_line)
                    print('I %s' % line)
                continue
                
            if pairmode and line and outtext and outtext[-1]:
                # session title comes in 2 lines and occurs several times - search for repeating line-pairs
                # this can be turned off with pairmode = False to improve performance
                line_pair = '%s\n%s' % (outtext[-1], line)
                responsetext = add_to_list(line_pair, line_pairs, del_line_pairs)
                if responsetext and verbose > 5:
                    print(responsetext)
            outtext.append(line)
            
    
    fulltext = '\n'.join(outtext)+'\n'
    # delete repeated line-pairs
    for line_pair in del_line_pairs:
        try:
            fulltext = re.sub(line_pair,'',fulltext)
        except:
            print('failed to delete line_pair:')
            print(line_pair, '\n')
    return fulltext

def clean_linebreaks(fulltext):
    """
    delete linebreak out of page-ranges
    to prevent refextract deleting hyphens at the end of a line
    """
    import re
    
    fulltext = re.sub(r'(\d)-\n(\d)', r'\1-\2', fulltext)
    return fulltext
    

def get_reference_section(fulltext, start_tag='REFERENCES', item_tag='[1]'):
    """
    Very simple extraction of reference section without garbage.
    """
    import re
    
    # find the start tag, and get rid of leading text
    start_pos = fulltext.upper().find('\n%s\n' % start_tag)
    fulltext = fulltext[start_pos:]
    # find the first item, and get rid of leading garbage
    start_pos = fulltext.upper().find('\n%s' % item_tag)
    fulltext = fulltext[start_pos:]
    
    #delete linebreak preserving hyphen
    fulltext = re.sub('\n', ' ',fulltext)
    #add linebreak in front of item
    fulltext = re.sub(r'(\[\d+\])', r'\n\1', fulltext)
    #replace ;
    fulltext = re.sub(';', ',',fulltext)
    
    return '%s\n%s' % (start_tag, fulltext)
    
def main():
    import codecs
    import sys
    
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = 'mo1a02'
    infile = codecs.EncodedFile(codecs.open('%s.txt' % fname),'utf8')
    outfile = codecs.EncodedFile(codecs.open('%s_out.txt' % fname,mode='wb'),'utf8')
    
    fulltext = clean_fulltext_jacow(infile.readlines(), verbose=6)
    fulltext = clean_linebreaks(fulltext)
    fulltext = re.sub('&','&amp;',fulltext)
    outfile.write(fulltext)
    outfile.close()
    
    
if __name__ == "__main__":
    main()
