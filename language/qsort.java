import java.util.*;
import java.io.*;

public class qsort {

    static long  ctm = 0;

    static void output(Object o)
    {
        System.out.println(o);
    }

    static void log(Object o)
    {
        System.out.println(o);
    }

    static void sort(int[] v) {
        int n = v.length;
        sort(v, 0, n - 1);
    }

    static double click() {
        long c = System.currentTimeMillis();
        double v = ((double)(c - ctm)) / 1000.0;
        ctm = c;
        return v;
    }

    static void sort(int[] v, int start, int end) {
        if (start >= end)
            return;
        int m = (start + end)/2;
        int pivot = v[m];
        int t;
        if (m < end) {
            t = v[m];
            v[m] = v[end];
            v[end] = t;
        }
        m = start;
        for (int i = start; i < end; i++) {
            if (v[i] < pivot) {
                t = v[i];
                v[i] = v[m];
                v[m] = t;
                m++;
            }
        }
        t = v[m];
        v[m] = v[end];
        v[end] = t;
        sort(v, start, m - 1);
        sort(v, m + 1, end);
    }

    public static void main(String[] args) {
        try {
            click();
            BufferedReader br = new BufferedReader(new FileReader(args[0]));
            String s;
            ArrayList<Integer> ial = new ArrayList<Integer>();
            while ((s = br.readLine()) != null) {
                String[] t = s.split("\\s");
                for (String i : t) {
                    ial.add(Integer.parseInt(i));
                }
            }
            output("load: " + click());

            int size = ial.size();
            int[] v = new int[size];
            for (int i = 0; i < size; i++) {
                v[i] = ial.get(i).intValue();
            }

            click();
            int[] v2 = new int[size];
            for (int i = 0; i < size; i++) {
                v2[i] = v[i];
            }
            output("duplicate: " + click());

            click();
            sort(v);
            output("qsort: " + click());


            click();
            for (int i = 0; i < size; i++) {
                if (v[i] != i) {
                    output("fail to validate");
                    break;
                }
            }
            output("validate: " + click());

            ArrayList<Integer> ial2 = new ArrayList<Integer>(ial);
            click();
            Collections.sort(ial2);
            output("ArrayList.sort: " + click());


        }
        catch (IOException e) {
            output(e);
        }
    }
}

