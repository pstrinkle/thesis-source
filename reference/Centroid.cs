using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace TrinkleClusteringEngine
{
    class Centroid
    {
        public Centroid(string docName, Dictionary<string, double> dv)
        {
            this.name = new StringBuilder(256);
            this.vectorCnt = 0;
            this.centroidVector = new Dictionary<string, double>(2000);
            this.length = 0.00;
            this.addDocumentVectorToCentroid(docName, 1, dv);
        }

        public Centroid(Centroid c)
        {
            // perform deep copy
            this.name = new StringBuilder(c.getName());
            this.vectorCnt = c.getVectorCnt();
            this.centroidVector = new Dictionary<string, double>(c.getCentroidVector());
            this.length = c.getLength();
        }

        static public double similarity(Centroid a, Centroid b)
        {
            Dictionary<string, double> vectorA = a.getCentroidVector();
            Dictionary<string, double> vectorB = b.getCentroidVector();
            
            double lengthA = a.getLength();
            double lengthB = b.getLength();

            double dotproduct = 0.0;

            // compute dot product of vectors A & B
            foreach (KeyValuePair<string, double> kvp in vectorA)
            {
                // if both vectors have the key
                if (vectorB.ContainsKey(kvp.Key))
                {
                    dotproduct += (kvp.Value * vectorB[kvp.Key]);
                }
            }

            return (dotproduct / (lengthA * lengthB));
        }

        public void addDocumentVectorToCentroid(string docName, int addCnt, Dictionary<string, double> newDocVec)
        {
            // determine the weight of the merging pieces
            double oldWeight = (double)this.vectorCnt / (this.vectorCnt + addCnt);
            double newWeight = (double)addCnt / (this.vectorCnt + addCnt);

            if (this.name.Length == 0)
            {
                this.name.Append(docName);
            }
            else
            {
                this.name.Append("," + docName);
            }

            // calculate new centroid
            List<string> centroidTerms = new List<string>(this.centroidVector.Keys);

            // reduce weight of values already in vector
            foreach (string key in centroidTerms)
            {
                if (newDocVec.ContainsKey(key))
                {
                    // if is in both vectors!
                    double oldValue = this.centroidVector[key] * oldWeight;
                    double newValue = newDocVec[key] * newWeight;

                    this.centroidVector[key] = oldValue + newValue;

                    // so when we go through to add in all the missing ones we won't have excess
                    newDocVec.Remove(key);
                }
                else // if it is strictly in the old vector
                {
                    double oldValue = this.centroidVector[key] * oldWeight;

                    this.centroidVector[key] = oldValue;
                }
            }

            // add new values to vector
            foreach (KeyValuePair<string, double> kvp in newDocVec)
            {
                // we don't so we'll have to create a new value with the weight of the added vector
                double newValue = kvp.Value * newWeight;

                this.centroidVector.Add(kvp.Key, newValue);
            }

            this.vectorCnt += addCnt;

            this.length = 0;

            // calculate magnitude
            foreach (KeyValuePair<string, double> kvp in this.centroidVector)
            {
                this.length += (kvp.Value * kvp.Value);
            }

            this.length = Math.Sqrt(this.length);
        }

        public string getName()
        {
            return this.name.ToString();
        }

        public double getLength()
        {
            return this.length;
        }

        public int getVectorCnt()
        {
            return this.vectorCnt;
        }

        public Dictionary<string, double> getCentroidVector()
        {
            return new Dictionary<string, double>(this.centroidVector);
        }

        private Dictionary<string, double> centroidVector;

        private int vectorCnt;
        private StringBuilder name;
        private double length;
    }
}
