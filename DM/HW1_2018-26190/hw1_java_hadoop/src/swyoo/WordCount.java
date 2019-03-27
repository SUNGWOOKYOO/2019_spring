package swyoo;

import java.io.File;
import java.io.IOException;
import java.util.StringTokenizer;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class WordCount {
	public static class TokenizerMapper extends Mapper<Object, Text, Text, IntWritable> {
		private final static IntWritable one = new IntWritable(1);
		private Text word = new Text();

		@Override
		public void map(Object key, Text value, Mapper<Object, Text, Text, IntWritable>.Context context)
				throws IOException, InterruptedException {
			System.out.println("=============================================================");
			System.out.println("			Map fuction ...			");
			System.out.println("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =");

//			System.out.println("==================================================================");
//			System.out.print("DEBUG::: ");
//			System.out.println();
//			System.out.println("==================================================================");

			StringTokenizer itr = new StringTokenizer(value.toString());
			while (itr.hasMoreTokens()) {
				word.set(itr.nextToken());
				System.out.println("=                                                           =");
				System.out.println("=    Context.write(word, one): " + word + " " + one + "		");
				System.out.println("=                                                           =");
				context.write(word, one);
			}
			System.out.println("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =");
			System.out.println("			Map fuction END			");
			System.out.println("=============================================================");
		}
	}

	public static class IntSumReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
		private IntWritable result = new IntWritable();

		@Override
		public void reduce(Text key, Iterable<IntWritable> values,
				Reducer<Text, IntWritable, Text, IntWritable>.Context context)
				throws IOException, InterruptedException {
			// TODO Auto-generated method stub
			System.out.println("=============================================================");
			System.out.println("			Reduce fuction ...			");
			System.out.println("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =");
			int sum = 0;
			for (IntWritable val : values) {
				sum += val.get();
			}
			result.set(sum);
			context.write(key, result);
			System.out.println("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =");
			System.out.println("			Reduce fuction END			");
			System.out.println("=============================================================");
		}
	}

	@SuppressWarnings("deprecation")
	public static void main(String[] args) throws IOException, ClassNotFoundException, InterruptedException {

		Configuration conf = new Configuration();
		String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
		if (otherArgs.length != 2) {
			System.err.println("Usage: wordcount <in> <out>");
			System.exit(2);
		}
		
		// delete previous result file
		File fs = new File(otherArgs[1]);
		if (fs.exists()) {
			Tool tool = new Tool();
			tool.filedelete(otherArgs[1]);
		}

		Job job = new Job(conf, "word count");
		job.setJarByClass(WordCount.class);
		job.setMapperClass(TokenizerMapper.class);
		job.setReducerClass(IntSumReducer.class);
		job.setOutputKeyClass(Text.class);
		job.setOutputValueClass(IntWritable.class);
		// job.setMapOutputKeyClass(Text.class);
		// job.setMapOutputValueClass(IntWritable.class);
//		job.setNumReduceTasks(2); // the # of computer that will be distributed
		job.setNumReduceTasks(1);

		System.out.println("==================================================================");
		System.out.println("			DEBUG 			");
		System.out.println("==================================================================");

		FileInputFormat.addInputPath(job, new Path(otherArgs[0]));

		/*
		 * System.out.println(
		 * "==================================================================");
		 * System.out.print("DEBUG::: "); System.out.println(); System.out.println(
		 * "==================================================================");
		 */

		FileOutputFormat.setOutputPath(job, new Path(otherArgs[1]));
		System.exit(job.waitForCompletion(true) ? 0 : 1);

		System.out.println("==================================================================");
		System.out.println("			DEBUG END			");
		System.out.println("==================================================================");
	}
}
