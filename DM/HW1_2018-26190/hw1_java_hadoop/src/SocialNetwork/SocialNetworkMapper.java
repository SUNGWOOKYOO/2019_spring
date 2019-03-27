package SocialNetwork;

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class SocialNetworkMapper extends Mapper<Object, Text, Text, Text> {
	public Text key = new Text();
	public Text element = new Text();

	@Override
	protected void map(Object map_key, Text value, Mapper<Object, Text, Text, Text>.Context context)
			throws IOException, InterruptedException {

		// TODO Auto-generated method stub
		System.out.println("================= Mapper Start! =====================");
		StringTokenizer tokenizer = new StringTokenizer(value.toString());
		StringBuilder keystr = new StringBuilder();

		if (tokenizer.hasMoreTokens()) {
			tokenizer.nextToken();
			if (tokenizer.hasMoreTokens()) {
				key.set(tokenizer.nextToken());
				element.set("1");
				context.write(key, element);
				System.out.println(key.toString() + ", " + element.toString());
			}
		}
		System.out.println("================= Mapper end! =====================");
	}
}
