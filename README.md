# zones

This is the repository where we track our DNS zone files

## Instructions to add records

The way that you update a configuration is as follows:

1. Clone down the repository locally to your computer
2. Add the changes you want (remember to add reverse DNS entries if you are adding A or AAAA records)
3. Run `./update_serial.py` which auto increments serials for all zone files
4. Run `./check_zones.py` to check your work
5. Commit & Push your changes with a meaningful Git message. For example, "Serial 126, added random.cosi.clarkson.edu"
6. Create a pull request and ask two reviewers to approve your work

The webhook attached to this repo should trigger Talos to pull down and load any changes. However if this fails:

1. Log into TalDOS and **become root**
2. `cd /etc/nsd/zones`
3. `git pull`
4. `systemctl reload nsd`

If you are going to do it a different way, please make sure that you update the Git server with the newest version of the configuration, and be sure to make it so that we only need to "fast forward" on the DNS server itself.

## Other notes

`dns01.cosi.clarkson.edu` and `dns02.cosi.clarkson.edu` are glue records from Clarkson's nameservers, for `128.153.145.3` and `128.153.145.4`, respectively. 128.153.145.4 should *not* be used for any other purpose than a legitimate DNS server.

## Considerations

Remember that this DNS is propogated back to the public DNS servers. Please keep the record names apropriate. If you even slightly question the name, please contact a lab director for their input.
