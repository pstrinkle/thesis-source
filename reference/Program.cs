using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace TrinkleClusteringEngine
{
    class Program
    {
        static void Main(string[] args)
        {
            StringBuilder dictpath = new StringBuilder(256);
            StringBuilder postingpath = new StringBuilder(256);
            // keyed on term returns dictionary with docIDs as keys for tf-idf
            Dictionary<string, Dictionary<string, double>> termdocmatrix = new Dictionary<string, Dictionary<string, double>>(2000);
            int documentCnt = 0; // this is used to help with memory estimation
            char[] delim = { '+' };

            DateTime start = DateTime.Now;

            if (args.Length != 2)
            {
                System.Console.WriteLine("Invalid Parameters: <dictionaryfile.txt> <postingsfile.txt>");
                return;
            }
            else
            {
                dictpath.Append(args[0]);
                postingpath.Append(args[1]);
            }

            int recordSize = 22;

            // read in dictionary and postings file
            // build term document matrix
            #region BuildTermDocMatrix
            StreamReader dictFile = new StreamReader(dictpath.ToString());
            FileStream postingslist = new FileStream(postingpath.ToString(), FileMode.Open);

            string dictline = "";

            // read in dictionary line by line (each line is a record of fixed length)
            while ((dictline = dictFile.ReadLine()) != null)
            {
                // 35 chars for term + ":" + 5 for df + ":" + 7 index into posting list
                string dictterm = dictline.Substring(0, 35).Trim();
                dictline = dictline.Remove(0, 36);
                int docFreq = Int32.Parse(dictline.Substring(0, 5).Trim());
                dictline = dictline.Remove(0, 6);
                int posting_index = Int32.Parse(dictline.Substring(0, 7).Trim());

                //Console.WriteLine(dictterm + " : " + posting_index.ToString());

                // the postings entries are in the order of the dictionary terms
                byte[] record = new byte[recordSize * docFreq];

                postingslist.Read(record, 0, recordSize * docFreq);

                string record_as_string = System.Text.ASCIIEncoding.ASCII.GetString(record);

                int recordCnt = record_as_string.Length / recordSize;

                Dictionary<string, double> doctfidf = new Dictionary<string, double>(5);

                // split the records into pieces
                for (int i = 0; i < recordCnt; i++)
                {
                    string tmprecord = record_as_string.Substring(0, 20);
                    record_as_string = record_as_string.Remove(0, 22);

                    string docID = tmprecord.Substring(0, 10).Trim();
                    double tfidf = Double.Parse(tmprecord.Substring(11, 9).Trim());

                    //Console.WriteLine("DocID: " + docID + " Tf-idf: " + tfidf.ToString());

                    doctfidf.Add(docID, tfidf);
                }

                termdocmatrix.Add(dictterm, doctfidf);
            }

            postingslist.Close();
            dictFile.Close();
            #endregion

            // build document vectors from term document matrix
            #region TermDocumentMatrix
            Dictionary<string, Dictionary<string, double>> documentvectors = new Dictionary<string, Dictionary<string, double>>(200);

            foreach (KeyValuePair<string, Dictionary<string, double>> kvp in termdocmatrix)
            {
                //Console.WriteLine(kvp.Key);

                // kvp.Key is the term
                // subkvp.Key is the document ID
                // subkvp.Value is the tf-idf for the term

                foreach (KeyValuePair<string, double> subkvp in kvp.Value)
                {
                    //Console.WriteLine("DocID: " + subkvp.Key + " Tf-idf: " + subkvp.Value.ToString());

                    // this is not a new document vector
                    if (documentvectors.ContainsKey(subkvp.Key))
                    {
                        documentvectors[subkvp.Key].Add(kvp.Key, subkvp.Value);
                    }
                    else
                    {
                        // build new document vector
                        documentvectors.Add(subkvp.Key, new Dictionary<string, double>());
                        documentvectors[subkvp.Key].Add(kvp.Key, subkvp.Value);
                    }
                }
            }

            // free some memory
            termdocmatrix.Clear();
            #endregion

            // build centroids (initially all documents are in trivial centroids)
            Dictionary<string, Centroid> centroids = new Dictionary<string, Centroid>(documentvectors.Count);

            foreach (KeyValuePair<string, Dictionary<string, double>> kvp in documentvectors)
            {
                centroids.Add(kvp.Key, new Centroid(kvp.Key, kvp.Value));
                documentCnt++;
            }

            // free some memory
            documentvectors.Clear();

            // For Information Only
            #region BuildAndCompareCorpusCentroid
            List<string> centroidKeys = new List<string>(centroids.Keys);
            Centroid forCorpus = new Centroid(centroids[centroidKeys[0]]); // this method preserves Centroid details

            // we used entry 0 to make the first entry
            for (int i = 1; i < centroidKeys.Count; i++)
            {
                forCorpus.addDocumentVectorToCentroid(centroidKeys[i], centroids[centroidKeys[i]].getVectorCnt(), centroids[centroidKeys[i]].getCentroidVector());
            }

            double maxSim = -1;
            string maxName = string.Empty;

            foreach (KeyValuePair<string, Centroid> kvp in centroids)
            {
                double sim = Centroid.similarity(kvp.Value, forCorpus);

                if (sim > maxSim)
                {
                    maxSim = sim;
                    maxName = kvp.Key;
                }
            }

            Console.WriteLine("Most Similar to Corpus: " + maxName + " with similarity: " + maxSim.ToString());

            #endregion

            // so I need a matrix that is just an upper triangle matrix.
            Dictionary<string, double> similarities = new Dictionary<string, double>(2000);

            // centroids is the hash table of all centroids keyed on centroid name

            // So I can track how many similarity checks I do
            int cnt = 0;

            // Compute Initial Similarity Matrix (Upper Triangle Matrix with no Diagonals)
            #region InitialCompute
            List<string> cen = new List<string>(centroids.Keys);
            for (int i = 0; i < cen.Count; i++)
            {
                for (int j = i + 1; j < cen.Count; j++)
                {
                    cnt++;

                    double sim = Centroid.similarity(centroids[cen[i]], centroids[cen[j]]);

                    similarities.Add(cen[i] + " + " + cen[j], sim);
                }
            } // for each centroid go along by row then column
            #endregion

            Console.WriteLine("Number of Initial Similarity Calculations: " + cnt.ToString());

            #region DetermineMostAndLeastSimilar
            // Run through initial similarity scores seeking out the largest and smallest
            double mostSimVal = -1;
            string mostSimName = string.Empty;
            double leastSimVal = 2;
            string leastSimName = string.Empty;

            foreach (KeyValuePair<string, double> kvp in similarities)
            {
                if (kvp.Value > mostSimVal)
                {
                    mostSimVal = kvp.Value;
                    mostSimName = kvp.Key;
                }

                if (kvp.Value < leastSimVal)
                {
                    leastSimVal = kvp.Value;
                    leastSimName = kvp.Key;
                }
            }

            Console.WriteLine("Most Similar Documents: " + mostSimName + " with similarity: " + mostSimVal.ToString());
            Console.WriteLine("Least Similar Documents: " + leastSimName + " with similarity: " + leastSimVal.ToString());

            #endregion

            #region ClusterAllDocuments
            while (centroids.Count > 1)
            {
                // so I know who I'm joining
                string maxI = string.Empty;
                string maxJ = string.Empty;
                double maxValue = -1;

                // Find max Similarity
                foreach (KeyValuePair<string, double> kvp in similarities)
                {
                    if (kvp.Value > maxValue)
                    {
                        maxValue = kvp.Value;
                        string[] names = kvp.Key.Split(delim);

                        maxI = names[0].Trim();
                        maxJ = names[1].Trim();
                    }
                }

                Console.WriteLine("Merging: " + maxI + " and " + maxJ + " of similarity: " + maxValue.ToString());

                if (String.Compare(maxI, string.Empty) == 0)
                {
                    Console.WriteLine("Emptry String detected, centroids in system:" + centroids.Count.ToString());                    
                    
                    break;
                }

                // New Centroid -- When creating Centroid with Centroid it preserves the VectorCount and Such
                Centroid centroid_x = new Centroid(centroids[maxI]);
                centroid_x.addDocumentVectorToCentroid(centroids[maxJ].getName(), centroids[maxJ].getVectorCnt(), centroids[maxJ].getCentroidVector());
                // when you merge two centroids the weight of the centroid being added is reduced completely...
                // need to consider fixing (luckily this will be abstracted away

                // Remove Ones I just merged from the list
                centroids.Remove(maxI);
                centroids.Remove(maxJ);

                // Remove all references in similarlity Table
                List<string> valuesToRemove = new List<string>(2 * documentCnt);
                foreach (string k in similarities.Keys)
                {
                    string[] names = k.Split(delim);

                    string name_i = names[0].Trim();
                    string name_j = names[1].Trim();

                    if (String.Compare(name_i, maxI) == 0
                        || String.Compare(name_i, maxJ) == 0
                        || String.Compare(name_j, maxI) == 0
                        || String.Compare(name_j, maxJ) == 0)
                    {
                        valuesToRemove.Add(k);
                    }
                }

                // Clean out Similarity Values
                foreach (string r in valuesToRemove)
                {
                    similarities.Remove(r);
                }

                // Calculate New similarity of everyone against new Centroid
                foreach (string k in centroids.Keys)
                {
                    double sim = Centroid.similarity(centroids[k], centroid_x);
                    cnt++;

                    similarities.Add(centroids[k].getName() + " + " + centroid_x.getName(), sim);
                }

                // add new centroid to x
                centroids.Add(centroid_x.getName(), centroid_x);
            }
            #endregion

            Console.WriteLine("Final Number of Similarity Calculations made: " + cnt.ToString());

            DateTime stop = DateTime.Now;
            Console.WriteLine("Total time: " + (stop - start).ToString());
        }
    }
}
