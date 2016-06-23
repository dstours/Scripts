#!/usr/bin/env python
import sys
import traceback

def usage():
    print "usage: %s input.csv output.txt" % sys.argv[0]

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

def main():

    if len(sys.argv) < 3:
        usage()
        sys.exit(-1)

    infile = sys.argv[1]
    outfile = sys.argv[2]

    print 'Converting file "%s" and saving contents to "%s"' % (infile, outfile)

    outf = None
    try:
        # The count is for changing the format for Headers
        count = 0
        outf = open(outfile, 'w')

        with open(infile, 'r') as inf:
            for line in inf:
                # If count is 0, it's the Header
                if count == 0:
                    tmp = '||' + line.strip().replace(',', '||') + '||'
                    outf.write(tmp + '\n')
                    
                    # Disable Header formatting for the CSV data
                    count = 1

                else:
                    # Convert all commas to pipes
                    tmp = '|' + line.strip().replace(',', '|') + '|'
                        
                    # Search for all instances of |
                    places = find(tmp, '|')
                    
                    # The default index(base 0) 
                    DEFAULT_CORRECT = 1

                    # There should always be 12 pipes if we follow the format
                    # So if there are more than 12 pipes in a line, we know 
                    # that some commas in the Title column were accidentally
                    # converted
                    count = tmp.count('|')
                    
                    # Find modulo
                    if count > 12:
                        diff = count % 12
                    
                    # For each extra pipe we find, we can assume that every
                    # pipe after the second pipe is actually a mistake
                    # so what we do is turn the entire line into a list and
                    # convert the modulo pipes back to commas
                        for i in diff:
                            tmp2[places[DEFAULT_CORRECT + (i+1)]] = ','                        
                    
                    # Convert the list back to a string
                    tmp2 = list(tmp)
                    tmp2 = ''.join(tmp2)
                    outf.write(tmp2 + '\n')
                        
    except Exception, e:
        traceback.print_exc()
        sys.exit(-1)

    finally:
        if outf:
            outf.close()

    print 'Conversion Complete'

if __name__ == '__main__':
    main()
