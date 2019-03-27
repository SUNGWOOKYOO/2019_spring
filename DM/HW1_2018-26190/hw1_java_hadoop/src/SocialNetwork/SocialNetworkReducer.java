package SocialNetwork;

import java.io.IOException;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

public class SocialNetworkReducer extends Reducer<Text, Text, Text, Text>{
	public Text outputkey = new Text();
	public Text outputelement = new Text();
	@Override
	protected void reduce(Text key, Iterable<Text> values, Reducer<Text, Text, Text, Text>.Context context)
			throws IOException, InterruptedException {
		// TODO Auto-generated method stub
		System.out.println("================= Reducer Start! =====================");
		System.out.println("key: " + key);
		System.out.print("values: ");
		int sum = 0;
		for (Text val : values) {
			System.out.print(val + " ");
			int one  = Integer.parseInt(val.toString());
			sum = sum + one;
		}System.out.println();
		outputkey.set(key.toString());
		outputelement.set(Integer.toString(sum));
		context.write(outputkey, outputelement);
		
		System.out.println("================= Reducer End! =====================");
	}
}
