package SocialNetwork;

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class SocialNetworkMapper2 extends Mapper<Object, Text, Text, Text> {
	public Text key = new Text();
	public Text element = new Text();

	@Override
	protected void map(Object map_key, Text value, Mapper<Object, Text, Text, Text>.Context context)
			throws IOException, InterruptedException {
		// TODO Auto-generated method stub
		System.out.println("================= Map2 Start! =====================");
		System.out.println("Debug");
//		System.out.println("map_key: " + map_key.toString());
//		System.out.println("value: " + value.toString());
		StringTokenizer tokenizer = new StringTokenizer(value.toString());
		StringBuilder valstr = new StringBuilder();
		if (tokenizer.hasMoreTokens()) {
			valstr.append(tokenizer.nextToken() + "\t");
			if (tokenizer.hasMoreTokens()) {
				valstr.append(tokenizer.nextToken());
				element.set(valstr.toString());
				key.set("One");
				context.write(key, element);
				System.out.println(key.toString() + ", " + element.toString());
			}
		}
		System.out.println("================= Map2 End! =====================");
	}
}
