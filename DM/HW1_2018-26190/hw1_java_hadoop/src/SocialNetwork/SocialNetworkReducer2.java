package SocialNetwork;

import java.io.IOException;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

public class SocialNetworkReducer2 extends Reducer<Text, Text, NullWritable, Text> {
	// public Text outputkey = new Text();
	public Text outputelement = new Text();
	private int k;

	protected void setup(Context context) throws IOException, InterruptedException {
		Configuration config = context.getConfiguration();
		k = config.getInt("k", 10); // Default value is 10
	}

	@Override
	protected void reduce(Text key, Iterable<Text> values, Reducer<Text, Text, NullWritable, Text>.Context context)
			throws IOException, InterruptedException {
		// TODO Auto-generated method stub
		System.out.println("================= Reduce2 Start! =====================");
		System.out.println("key: " + key);

		// How to get sorted List?
		// https://howtodoinjava.com/sort/java-sort-map-by-values/
		Map<String, Integer> unsortedMap = new HashMap<>();
		LinkedHashMap<String, Integer> sortedMap = new LinkedHashMap<>();
		for (Text val : values) {
			System.out.println(val);
			String Info[] = val.toString().split("\t"); 
			//System.out.println(Info[1]); // # of follower
			unsortedMap.put(val.toString(), Integer.parseInt(Info[1]));
		}
		unsortedMap.entrySet().stream().sorted(Map.Entry.comparingByValue(Comparator.reverseOrder()))
				.forEachOrdered(x -> sortedMap.put(x.getKey(), x.getValue()));
		System.out.println("Sorted Map   : " + sortedMap);

		StringBuilder OutputInfo = new StringBuilder();
		int i = 0;
		System.out.println("top k: " + k);
		Iterator<String> it = sortedMap.keySet().iterator();
		while (it.hasNext() && (++i <= k)) {
			OutputInfo.append(it.next());
			if(i != k) {
				OutputInfo.append("\r\n");
				//System.out.println("iteration");
			}
		}
//		for (String s : ) {
//			  System.out.println(s);
//			  if(i++ >= k)
//				  break;
//			}
		// outputkey.set(key.toString());
		outputelement.set(OutputInfo.toString());
		context.write(NullWritable.get(), outputelement);
		System.out.println("================= Reduce2 Start! =====================");
	}
}
