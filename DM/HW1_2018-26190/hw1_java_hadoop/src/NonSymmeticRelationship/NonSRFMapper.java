package NonSymmeticRelationship;

import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class NonSRFMapper extends Mapper<Object, Text, Text, Text> {
	public Text key = new Text();
	public Text element = new Text();

	@Override
	protected void map(Object map_key, Text value, Mapper<Object, Text, Text, Text>.Context context)
			throws IOException, InterruptedException {
		// TODO Auto-generated method stub
		System.out.println("================= Mapper Start! =====================");
		StringTokenizer tokenizer = new StringTokenizer(value.toString());
		StringBuilder keystr = new StringBuilder();
		int id1 = 0, id2 = 0;
		if (tokenizer.hasMoreTokens()) {
			// keystr.append(tokenizer.nextToken() + " ");
			id1 = Integer.parseInt(tokenizer.nextToken());
		}
		if (tokenizer.hasMoreTokens()) {
			// keystr.append(tokenizer.nextToken());
			id2 = Integer.parseInt(tokenizer.nextToken());
		}
		if (id1 < id2) {
			keystr.append(Integer.toString(id1) + "\t" + Integer.toString(id2));
		} else {
			keystr.append(Integer.toString(id2) + "\t" + Integer.toString(id1));
		}
		key.set(keystr.toString());
		element.set("1");
		context.write(key, element);
		System.out.println(key.toString() + ", " + element.toString());
		System.out.println("================= Mapper End! =====================");
	}
}
